SELECT TOP 100 * FROM Raw_Loan_Data_1052;

CREATE TABLE CUSTOMER (
    CustomerID INT IDENTITY(1,1) PRIMARY KEY,
    CNIC VARCHAR(15) NOT NULL UNIQUE,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    PhoneNumber VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Address VARCHAR(255),
    DateRegistered DATE NOT NULL,
    EmploymentStatus VARCHAR(50),
    MonthlyIncome DECIMAL(18,2),
    CreditScore INT CHECK (CreditScore BETWEEN 300 AND 850)
);

CREATE TABLE LOAN_TYPE (
    LoanTypeID INT IDENTITY(1,1) PRIMARY KEY,
    TypeName VARCHAR(50) NOT NULL,
    InterestRate DECIMAL(5,2) NOT NULL CHECK (InterestRate > 0),
    DurationMonths INT NOT NULL
);

CREATE TABLE LOAN_APPLICATION (
    ApplicationID INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT NOT NULL FOREIGN KEY REFERENCES CUSTOMER(CustomerID),
    LoanTypeID INT NOT NULL FOREIGN KEY REFERENCES LOAN_TYPE(LoanTypeID),
    RequestedAmount DECIMAL(18,2) NOT NULL CHECK (RequestedAmount > 0),
    ApplicationDate DATE NOT NULL,
    Status VARCHAR(20) DEFAULT 'Approved'
);

CREATE TABLE LOAN (
    LoanID INT IDENTITY(1,1) PRIMARY KEY,
    ApplicationID INT NOT NULL FOREIGN KEY REFERENCES LOAN_APPLICATION(ApplicationID),
    CustomerID INT NOT NULL FOREIGN KEY REFERENCES CUSTOMER(CustomerID),
    ApprovedAmount DECIMAL(18,2) NOT NULL CHECK (ApprovedAmount > 0),
    LoanStartDate DATE NOT NULL,
    LoanEndDate DATE NOT NULL,
    IsRescheduled BIT DEFAULT 0, -- 1 for Yes, 0 for No
    ReasonForDefault VARCHAR(100),
    CONSTRAINT CHK_Dates CHECK (LoanEndDate > LoanStartDate)
);


CREATE TABLE COLLATERAL (
    CollateralID INT IDENTITY(1,1) PRIMARY KEY,
    LoanID INT NOT NULL FOREIGN KEY REFERENCES LOAN(LoanID),
    AssetType VARCHAR(50) NOT NULL,
    EstimatedValue DECIMAL(18,2) NOT NULL
);


CREATE TABLE PAYMENT (
    PaymentID INT IDENTITY(1,1) PRIMARY KEY,
    LoanID INT NOT NULL FOREIGN KEY REFERENCES LOAN(LoanID),
    InstallmentNumber INT NOT NULL,
    DueDate DATE NOT NULL,
    PaymentDate DATE NULL, -- CHANGED: Now allows NULL for pending future payments
    ScheduledAmount DECIMAL(18,2) NOT NULL,
    PaymentAmount DECIMAL(18,2) NOT NULL CHECK (PaymentAmount >= 0), -- CHANGED: Now allows 0 for pending payments
    PaymentMethod VARCHAR(50),
    LatePaymentFine DECIMAL(18,2) DEFAULT 0
);

CREATE TABLE AUDIT_LOG (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    TableName VARCHAR(50) NOT NULL,
    ActionType VARCHAR(100) NOT NULL,
    RecordID INT NOT NULL,
    ActionDate DATETIME DEFAULT GETDATE(),
    OldValue VARCHAR(MAX),
    NewValue VARCHAR(MAX)
);

INSERT INTO CUSTOMER (CNIC, FirstName, LastName, PhoneNumber, Email, Address, DateRegistered, EmploymentStatus, MonthlyIncome, CreditScore)
SELECT DISTINCT CNIC, FirstName, LastName, PhoneNumber, Email, Address, DateRegistered, EmploymentStatus, MonthlyIncome, CreditScore
FROM Raw_Loan_Data_1052
WHERE CNIC IS NOT NULL;


INSERT INTO LOAN_TYPE (TypeName, InterestRate, DurationMonths)
SELECT DISTINCT LoanTypeName, InterestRate, LoanDurationMonths
FROM Raw_Loan_Data_1052
WHERE LoanTypeName IS NOT NULL;


INSERT INTO LOAN_APPLICATION (CustomerID, LoanTypeID, RequestedAmount, ApplicationDate, Status)
SELECT DISTINCT c.CustomerID, lt.LoanTypeID, r.RequestedAmount, r.ApplicationDate, 'Approved'
FROM Raw_Loan_Data_1052 r
JOIN CUSTOMER c ON r.CNIC = c.CNIC
JOIN LOAN_TYPE lt ON r.LoanTypeName = lt.TypeName AND r.InterestRate = lt.InterestRate AND r.LoanDurationMonths = lt.DurationMonths
WHERE r.RequestedAmount IS NOT NULL;

INSERT INTO LOAN (ApplicationID, CustomerID, ApprovedAmount, LoanStartDate, LoanEndDate, IsRescheduled, ReasonForDefault)
SELECT DISTINCT 
    a.ApplicationID, 
    c.CustomerID, 
    r.ApprovedAmount, 
    r.LoanStartDate, 
    r.LoanEndDate, 
    CASE WHEN CAST(r.IsRescheduled AS VARCHAR(10)) IN ('Yes', '1', 'True') THEN 1 ELSE 0 END, 
    r.ReasonForDefault
FROM Raw_Loan_Data_1052 r
JOIN CUSTOMER c ON r.CNIC = c.CNIC
JOIN LOAN_APPLICATION a ON a.CustomerID = c.CustomerID AND a.RequestedAmount = r.RequestedAmount AND a.ApplicationDate = r.ApplicationDate
WHERE r.ApprovedAmount IS NOT NULL;


INSERT INTO COLLATERAL (LoanID, AssetType, EstimatedValue)
SELECT DISTINCT l.LoanID, r.CollateralAssetType, r.CollateralEstimatedValue
FROM Raw_Loan_Data_1052 r
JOIN CUSTOMER c ON r.CNIC = c.CNIC
JOIN LOAN l ON l.CustomerID = c.CustomerID AND l.ApprovedAmount = r.ApprovedAmount AND l.LoanStartDate = r.LoanStartDate
WHERE r.CollateralAssetType IS NOT NULL AND r.CollateralAssetType != 'None';

INSERT INTO PAYMENT (LoanID, InstallmentNumber, DueDate, PaymentDate, ScheduledAmount, PaymentAmount, PaymentMethod, LatePaymentFine)
SELECT DISTINCT 
    l.LoanID, 
    r.InstallmentNumber, 
    r.DueDate, 
    r.PaymentDate, 
    r.ScheduledInstallmentAmount, 
    r.PaymentAmount, 
    r.PaymentMethod, 
    r.LatePaymentFine
FROM Raw_Loan_Data_1052 r
JOIN CUSTOMER c ON r.CNIC = c.CNIC
JOIN LOAN l ON l.CustomerID = c.CustomerID 
WHERE r.InstallmentNumber IS NOT NULL;


SELECT * FROM CUSTOMER;

SELECT * FROM LOAN_TYPE;

SELECT * FROM LOAN_APPLICATION;

SELECT * FROM LOAN;

SELECT * FROM COLLATERAL;

SELECT * FROM PAYMENT;

SELECT * FROM AUDIT_LOG;

