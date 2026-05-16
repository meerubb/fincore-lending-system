CREATE OR ALTER TRIGGER trg_Audit_Loan_Updates
ON LOAN
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

   
    IF UPDATE(ApprovedAmount)
    BEGIN
      
        INSERT INTO AUDIT_LOG (TableName, ActionType, RecordID, ActionDate, OldValue, NewValue)
        SELECT 
            'LOAN', 
            'UPDATE - Approved Amount', 
            CAST(i.LoanID AS VARCHAR(50)), 
            GETDATE(),                     
            CAST(d.ApprovedAmount AS VARCHAR(50)), 
            CAST(i.ApprovedAmount AS VARCHAR(50))
        FROM inserted i
        JOIN deleted d ON i.LoanID = d.LoanID
        WHERE i.ApprovedAmount <> d.ApprovedAmount;
    END


    IF UPDATE(IsRescheduled)
    BEGIN
        
        INSERT INTO AUDIT_LOG (TableName, ActionType, RecordID, ActionDate, OldValue, NewValue)
        SELECT 
            'LOAN', 
            'UPDATE - Reschedule Status', 
            CAST(i.LoanID AS VARCHAR(50)), 
            GETDATE(),                     
            CAST(d.IsRescheduled AS VARCHAR(10)), 
            CAST(i.IsRescheduled AS VARCHAR(10))
        FROM inserted i
        JOIN deleted d ON i.LoanID = d.LoanID
        WHERE i.IsRescheduled <> d.IsRescheduled;
    END
END;
GO




SELECT LoanID, ApprovedAmount, IsRescheduled FROM LOAN WHERE LoanID = 5;


UPDATE LOAN 
SET ApprovedAmount = 50000, IsRescheduled = 1
WHERE LoanID = 5;


SELECT * FROM AUDIT_LOG;




CREATE OR ALTER TRIGGER trg_Auto_Credit_Penalty
ON PAYMENT
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(LatePaymentFine)
    BEGIN
        UPDATE C

        SET C.CreditScore = CASE 
            WHEN C.CreditScore - 15 < 300 THEN 300 
            ELSE C.CreditScore - 15 
        END
        FROM CUSTOMER C
        JOIN LOAN L ON C.CustomerID = L.CustomerID
        JOIN inserted i ON L.LoanID = i.LoanID
        JOIN deleted d ON i.PaymentID = d.PaymentID
        WHERE i.LatePaymentFine > d.LatePaymentFine; 
    END
END;
GO



CREATE OR ALTER TRIGGER trg_Audit_Loan_Insertion
ON LOAN
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO AUDIT_LOG (TableName, ActionType, RecordID, ActionDate, OldValue, NewValue)
    SELECT 
        'LOAN', 
        'INSERT - New Loan Issued', 
        CAST(i.LoanID AS VARCHAR(50)), 
        GETDATE(), 
        'NULL', 
        'Amount: ' + CAST(i.ApprovedAmount AS VARCHAR(20)) + ' | CustID: ' + CAST(i.CustomerID AS VARCHAR(10))
    FROM inserted i;
END;
GO

select * from customers
