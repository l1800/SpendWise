-- Authentication migration for SQL Server.
-- Run once before starting the updated Flask app.
-- Register the manager account in the app first, then replace the email below and rerun.

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    IF COL_LENGTH('dbo.Users', 'role') IS NULL
    BEGIN
        ALTER TABLE dbo.Users
        ADD role NVARCHAR(20) NOT NULL
            CONSTRAINT DF_Users_role DEFAULT N'household' WITH VALUES;
    END;

    DECLARE @AdminEmail NVARCHAR(255) = N'REPLACE_WITH_MANAGER_EMAIL';

    IF @AdminEmail <> N'REPLACE_WITH_MANAGER_EMAIL'
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE email = @AdminEmail)
            THROW 51010, 'Manager email is not registered. Register first, then run this script again.', 1;

        UPDATE dbo.Users SET role = N'admin' WHERE email = @AdminEmail;
    END;

    COMMIT TRANSACTION;

    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = N'dbo' AND TABLE_NAME = N'Users' AND COLUMN_NAME = N'role';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
