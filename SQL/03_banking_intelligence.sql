
CREATE VIEW vw_Customer_Late_Fines
AS
SELECT 
    C.CNIC,
    C.FirstName + ' ' + C.LastName AS CustomerName,
    C.PhoneNumber,
    L.ApprovedAmount AS TotalLoanAmount,
    COUNT(P.PaymentID) AS TotalPaymentsMade,
    SUM(P.LatePaymentFine) AS TotalFinesAccumulated
FROM CUSTOMER C
JOIN LOAN L ON C.CustomerID = L.CustomerID
JOIN PAYMENT P ON L.LoanID = P.LoanID
GROUP BY 
    C.CNIC,
    C.FirstName,
    C.LastName,
    C.PhoneNumber,
    L.ApprovedAmount
HAVING SUM(P.LatePaymentFine) > 0;
GO



SELECT * FROM vw_Customer_Late_Fines
ORDER BY TotalFinesAccumulated DESC;



CREATE VIEW vw_Risk_Classification
AS
SELECT 
    CustomerID,
    CNIC,
    FirstName + ' ' + LastName AS FullName,
    CreditScore,
    MonthlyIncome,
    CASE 
        WHEN CreditScore >= 750 AND MonthlyIncome > 100000 THEN 'Low Risk'
        WHEN CreditScore >= 600 THEN 'Medium Risk'
        ELSE 'High Risk'
    END AS RiskLevel
FROM CUSTOMER;
GO

SELECT * FROM vw_Risk_Classification
WHERE RiskLevel = 'High Risk';




CREATE VIEW vw_Bank_Dashboard_Stats AS
SELECT 
    (SELECT COUNT(*) FROM CUSTOMER) AS TotalCustomers,
    (SELECT SUM(ApprovedAmount) FROM LOAN) AS TotalMoneyLent,
    (SELECT SUM(LatePaymentFine) FROM PAYMENT) AS TotalFinesAccumulated,
    (SELECT COUNT(*) FROM LOAN WHERE IsRescheduled = 1) AS RescheduledLoans,
    (SELECT COUNT(*) FROM COLLATERAL) AS SecuredLoans
GO

SELECT * FROM vw_Bank_Dashboard_Stats;




CREATE VIEW vw_Defaulter_Watchlist AS
SELECT 
    C.FirstName + ' ' + C.LastName AS DefaulterName,
    C.PhoneNumber,
    C.CreditScore,
    L.ApprovedAmount AS MoneyOwed,
    SUM(P.LatePaymentFine) AS TotalFines,
    COL.AssetType AS AssetToSeize,
    COL.EstimatedValue AS AssetValue
FROM CUSTOMER C
JOIN LOAN L ON C.CustomerID = L.CustomerID
JOIN PAYMENT P ON L.LoanID = P.LoanID
JOIN COLLATERAL COL ON L.LoanID = COL.LoanID
WHERE C.CreditScore < 600
GROUP BY 
    C.FirstName, C.LastName, C.PhoneNumber, C.CreditScore, 
    L.ApprovedAmount, COL.AssetType, COL.EstimatedValue
HAVING SUM(P.LatePaymentFine) > 10000;

select * from vw_Defaulter_Watchlist;

SELECT TOP 1 * FROM vw_Defaulter_Watchlist;



CREATE PROCEDURE sp_Add_Customer
    @CNIC VARCHAR(15),
    @FirstName VARCHAR(50),
    @LastName VARCHAR(50),
    @PhoneNumber VARCHAR(15),
    @Email VARCHAR(100),
    @Address VARCHAR(255),
    @EmploymentStatus VARCHAR(50),
    @MonthlyIncome DECIMAL(18,2),
    @CreditScore INT
AS
BEGIN
    SET NOCOUNT ON;
    
    
    INSERT INTO CUSTOMER (CNIC, FirstName, LastName, PhoneNumber, Email, Address, DateRegistered, EmploymentStatus, MonthlyIncome, CreditScore)
    VALUES (@CNIC, @FirstName, @LastName, @PhoneNumber, @Email, @Address, GETDATE(), @EmploymentStatus, @MonthlyIncome, @CreditScore);

   
    SELECT SCOPE_IDENTITY() AS NewCustomerID;
END;
GO




CREATE OR ALTER PROCEDURE sp_Apply_For_Loan
    @CustomerID INT,
    @RequestedAmount DECIMAL(18,2),
    @DurationMonths INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CreditScore INT, @MonthlyIncome DECIMAL(18,2), @MonthlyInstallment DECIMAL(18,2);
    DECLARE @NewAppID INT, @NewLoanID INT, @LoanType INT;

    SELECT @CreditScore = CreditScore, @MonthlyIncome = MonthlyIncome FROM CUSTOMER WHERE CustomerID = @CustomerID;

    IF @CreditScore IS NULL
    BEGIN
        SELECT 'REJECTED' AS Status, 'Error: Customer ID not found.' AS Message; RETURN;
    END

    SELECT TOP 1 @LoanType = LoanTypeID FROM LOAN_TYPE WHERE DurationMonths = @DurationMonths;
    IF @LoanType IS NULL SET @LoanType = 1;

    SET @MonthlyInstallment = @RequestedAmount / @DurationMonths;

    IF @CreditScore < 500
    BEGIN
        SELECT 'REJECTED' AS Status, 'Credit Score is below minimum 500.' AS Message; RETURN;
    END

    IF @MonthlyInstallment > (@MonthlyIncome * 0.40)
    BEGIN
        SELECT 'REJECTED' AS Status, 'Installment exceeds 40% of income.' AS Message; RETURN;
    END

    
    INSERT INTO LOAN_APPLICATION (CustomerID, LoanTypeID, RequestedAmount, ApplicationDate, Status)
    VALUES (@CustomerID, @LoanType, @RequestedAmount, CAST(GETDATE() AS DATE), 'Approved');
    SET @NewAppID = SCOPE_IDENTITY();
    

    INSERT INTO LOAN (ApplicationID, CustomerID, ApprovedAmount, LoanStartDate, LoanEndDate, IsRescheduled)
    VALUES (@NewAppID, @CustomerID, @RequestedAmount, CAST(GETDATE() AS DATE), CAST(DATEADD(MONTH, @DurationMonths, GETDATE()) AS DATE), 'False');
    

    SET @NewLoanID = SCOPE_IDENTITY();
    EXEC sp_Generate_EMI_Schedule @LoanID = @NewLoanID, @Principal = @RequestedAmount, @DurationMonths = @DurationMonths;

    SELECT 'APPROVED' AS Status, 'Loan issued & EMI Schedule generated!' AS Message;
END;
GO


CREATE OR ALTER PROCEDURE sp_Process_Payment
    @LoanID INT,
    @AmountPaid DECIMAL(18,2),
    @Method VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @NextInstallment INT;
    DECLARE @CalculatedDueDate DATETIME;
    DECLARE @ScheduledAmt DECIMAL(18,2);

   
    SELECT @NextInstallment = ISNULL(MAX(InstallmentNumber), 0) + 1 
    FROM PAYMENT 
    WHERE LoanID = @LoanID;
    
    SET @CalculatedDueDate = GETDATE();
    
    
    SET @ScheduledAmt = @AmountPaid;
    
    
    INSERT INTO PAYMENT (LoanID, InstallmentNumber, DueDate, ScheduledAmount, PaymentAmount, PaymentDate, PaymentMethod)
    VALUES (@LoanID, @NextInstallment, @CalculatedDueDate, @ScheduledAmt, @AmountPaid, GETDATE(), @Method);
    
END;
GO



CREATE OR ALTER PROCEDURE sp_Generate_EMI_Schedule
    @LoanID INT,
    @Principal DECIMAL(18,2),
    @DurationMonths INT,
    @AnnualInterestRate DECIMAL(5,2) = 15.00
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @MonthlyRate FLOAT = (@AnnualInterestRate / 100.0) / 12.0;
    DECLARE @EMI DECIMAL(18,2);
    DECLARE @Counter INT = 1;
    DECLARE @DueDate DATE = GETDATE();

    
    SET @EMI = @Principal * ( @MonthlyRate * POWER(1 + @MonthlyRate, @DurationMonths) ) 
               / ( POWER(1 + @MonthlyRate, @DurationMonths) - 1 );

    
    WHILE @Counter <= @DurationMonths
    BEGIN
        SET @DueDate = DATEADD(MONTH, 1, @DueDate);

        INSERT INTO PAYMENT (LoanID, InstallmentNumber, DueDate, ScheduledAmount, PaymentAmount, PaymentMethod)
        VALUES (@LoanID, @Counter, @DueDate, @EMI, 0, 'Pending');

        SET @Counter = @Counter + 1;
    END
END;
GO


