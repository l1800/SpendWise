"""
Run this script once to create the Budget_Plans table in smart_Encomy.
Uses the same connection settings as db_connection.py.
"""
import pyodbc

SERVER = 'D403-013'
DATABASE = 'smart_Encomy'
DRIVER = 'ODBC Driver 17 for SQL Server'

conn_string = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

SQL = """
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'Budget_Plans'
)
BEGIN
    CREATE TABLE dbo.Budget_Plans (
        plan_id         INT IDENTITY(1,1) PRIMARY KEY,
        user_id         INT NOT NULL,
        category_id     INT NOT NULL,
        year            INT NOT NULL,
        month           INT NOT NULL,
        planned_amount  FLOAT NOT NULL DEFAULT 0,
        created_at      DATETIME NOT NULL DEFAULT GETDATE(),

        CONSTRAINT FK_Budget_Plans_Users
            FOREIGN KEY (user_id) REFERENCES dbo.Users(user_id),
        CONSTRAINT FK_Budget_Plans_Categories
            FOREIGN KEY (category_id) REFERENCES dbo.Categories(category_id)
    );

    PRINT '=== Budget_Plans table created ===';
END
ELSE
BEGIN
    PRINT '=== Budget_Plans table already exists ===';
END
"""

try:
    conn = pyodbc.connect(conn_string, autocommit=True)
    cursor = conn.cursor()
    cursor.execute(SQL)
    print("Done.")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
