-- Safe, repeatable SQL Server demo seed for SpendWise.
-- Adds missing demo data only; it never deletes or rewrites user data.
-- Create demo@spendwise.local via /auth/register first, then run this script.

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    DECLARE @UserId INT;
    DECLARE @ExpenseTypeId INT;
    DECLARE @IncomeTypeId INT;
    DECLARE @MonthlyFrequencyId INT;
    DECLARE @RegularExpenseTypeId INT;
    DECLARE @FixedExpenseTypeId INT;
    DECLARE @MonthStart DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
    DECLARE @FamilySize INT = 4;

    IF NOT EXISTS (SELECT 1 FROM Category_Types WHERE category_type_name = N'expense')
        INSERT INTO Category_Types (category_type_name) VALUES (N'expense');
    IF NOT EXISTS (SELECT 1 FROM Category_Types WHERE category_type_name = N'income')
        INSERT INTO Category_Types (category_type_name) VALUES (N'income');

    SELECT @ExpenseTypeId = category_type_id FROM Category_Types WHERE category_type_name = N'expense';
    SELECT @IncomeTypeId = category_type_id FROM Category_Types WHERE category_type_name = N'income';

    IF @ExpenseTypeId IS NULL OR @IncomeTypeId IS NULL
        THROW 51000, 'Could not resolve expense/income category types.', 1;

    SELECT @UserId = user_id, @FamilySize = family_size
    FROM Users WHERE email = N'demo@spendwise.local';

    IF @UserId IS NULL
        THROW 51002, 'Register demo@spendwise.local in the app before running this seed.', 1;

    CREATE TABLE #CategorySeed (
        category_name NVARCHAR(100) NOT NULL PRIMARY KEY,
        category_description NVARCHAR(255) NOT NULL,
        amount_per_person FLOAT NOT NULL,
        is_essential BIT NOT NULL,
        is_fixed_cost BIT NOT NULL,
        max_cut_percent FLOAT NOT NULL,
        importance_score FLOAT NOT NULL
    );

    INSERT INTO #CategorySeed VALUES
        (N'שכירות / משכנתא', N'תשלום דיור חודשי', 1050, 1, 1, 0, 100),
        (N'חשבונות חשמל ומים', N'חשבונות בית שוטפים', 180, 1, 0, 20, 82),
        (N'ארנונה', N'תשלום עירוני תקופתי', 110, 1, 1, 0, 92),
        (N'מזון וסופרמרקט', N'קניות מזון ומוצרי בית', 520, 1, 0, 15, 78),
        (N'חינוך וילדים', N'מסגרות, צהרון וחוגים', 430, 1, 0, 10, 88),
        (N'רכב ותחבורה', N'דלק ותחבורה שוטפת', 220, 0, 0, 30, 58),
        (N'בריאות', N'רופאים, תרופות וטיפולים', 170, 1, 0, 5, 96),
        (N'ביגוד והנעלה', N'ביגוד והנעלה למשפחה', 120, 0, 0, 45, 42),
        (N'בילויים ומסעדות', N'פנאי ואוכל מחוץ לבית', 140, 0, 0, 60, 32),
        (N'צדקה ומעשרות', N'תרומות ומעשרות', 150, 0, 0, 25, 68),
        (N'חסכונות והשקעות', N'חיסכון חודשי והשקעות', 200, 0, 0, 50, 72),
        (N'תקשורת', N'אינטרנט וטלפונים', 85, 1, 0, 20, 74),
        (N'ריהוט וציוד לבית', N'ציוד לבית והחלפות', 90, 0, 0, 50, 38),
        (N'חופשות ונופש', N'חופשות ונופש משפחתי', 120, 0, 0, 65, 30),
        (N'הלוואות', N'החזרי הלוואות חודשיים', 330, 1, 1, 0, 100),
        (N'מתנות ושמחות', N'אירועים ומתנות', 90, 0, 0, 45, 48),
        (N'הוצאות שונות', N'הוצאות מזדמנות', 110, 0, 0, 35, 50);

    INSERT INTO Categories (category_name, category_type_id, category_description, created_at)
    SELECT s.category_name, @ExpenseTypeId, s.category_description, GETDATE()
    FROM #CategorySeed s
    WHERE NOT EXISTS (
        SELECT 1 FROM Categories c
        WHERE c.category_name = s.category_name AND c.category_type_id = @ExpenseTypeId
    );

    INSERT INTO Category_Standards
        (category_id, amount_per_person, is_essential, is_fixed_cost, rule_description, max_cut_percent)
    SELECT c.category_id, s.amount_per_person, s.is_essential, s.is_fixed_cost,
           s.category_description, s.max_cut_percent
    FROM #CategorySeed s
    JOIN Categories c ON c.category_name = s.category_name AND c.category_type_id = @ExpenseTypeId
    WHERE NOT EXISTS (SELECT 1 FROM Category_Standards cs WHERE cs.category_id = c.category_id);

    INSERT INTO User_Category_Preferences (user_id, category_id, importance_score, created_at, updated_at)
    SELECT @UserId, c.category_id, s.importance_score, GETDATE(), GETDATE()
    FROM #CategorySeed s
    JOIN Categories c ON c.category_name = s.category_name AND c.category_type_id = @ExpenseTypeId
    WHERE NOT EXISTS (
        SELECT 1 FROM User_Category_Preferences p
        WHERE p.user_id = @UserId AND p.category_id = c.category_id
    );

    INSERT INTO User_Category_Goal (user_id, category_id, target_amount, created_at, updated_at)
    SELECT @UserId, c.category_id, cs.amount_per_person * @FamilySize, GETDATE(), GETDATE()
    FROM Categories c
    JOIN Category_Standards cs ON cs.category_id = c.category_id
    WHERE c.category_type_id = @ExpenseTypeId
      AND EXISTS (SELECT 1 FROM #CategorySeed s WHERE s.category_name = c.category_name)
      AND NOT EXISTS (
          SELECT 1 FROM User_Category_Goal g
          WHERE g.user_id = @UserId AND g.category_id = c.category_id
      );

    IF NOT EXISTS (SELECT 1 FROM ExpenseTypes WHERE expenseTypeName = N'רגילה')
        INSERT INTO ExpenseTypes (expenseTypeName) VALUES (N'רגילה');
    IF NOT EXISTS (SELECT 1 FROM ExpenseTypes WHERE expenseTypeName = N'קבועה')
        INSERT INTO ExpenseTypes (expenseTypeName) VALUES (N'קבועה');
    IF NOT EXISTS (SELECT 1 FROM ExpenseTypes WHERE expenseTypeName = N'חד פעמית')
        INSERT INTO ExpenseTypes (expenseTypeName) VALUES (N'חד פעמית');
    IF NOT EXISTS (SELECT 1 FROM ExpenseTypes WHERE expenseTypeName = N'חירום')
        INSERT INTO ExpenseTypes (expenseTypeName) VALUES (N'חירום');

    IF NOT EXISTS (SELECT 1 FROM IncomeCategories WHERE category_name = N'משכורת')
        INSERT INTO IncomeCategories (category_name) VALUES (N'משכורת');
    IF NOT EXISTS (SELECT 1 FROM IncomeCategories WHERE category_name = N'עסק')
        INSERT INTO IncomeCategories (category_name) VALUES (N'עסק');
    IF NOT EXISTS (SELECT 1 FROM IncomeCategories WHERE category_name = N'קצבה')
        INSERT INTO IncomeCategories (category_name) VALUES (N'קצבה');
    IF NOT EXISTS (SELECT 1 FROM IncomeCategories WHERE category_name = N'הכנסה אחרת')
        INSERT INTO IncomeCategories (category_name) VALUES (N'הכנסה אחרת');

    IF NOT EXISTS (SELECT 1 FROM Income_Frequency WHERE frequency_name = N'חודשי')
        INSERT INTO Income_Frequency (frequency_name) VALUES (N'חודשי');
    IF NOT EXISTS (SELECT 1 FROM Income_Frequency WHERE frequency_name = N'חד פעמי')
        INSERT INTO Income_Frequency (frequency_name) VALUES (N'חד פעמי');

    SELECT @MonthlyFrequencyId = frequency_id FROM Income_Frequency WHERE frequency_name = N'חודשי';
    SELECT @RegularExpenseTypeId = expenseTypeId FROM ExpenseTypes WHERE expenseTypeName = N'רגילה';
    SELECT @FixedExpenseTypeId = expenseTypeId FROM ExpenseTypes WHERE expenseTypeName = N'קבועה';

    IF @MonthlyFrequencyId IS NULL OR @RegularExpenseTypeId IS NULL OR @FixedExpenseTypeId IS NULL
        THROW 51001, 'Could not resolve transaction lookup values.', 1;

    CREATE TABLE #IncomeSeed (
        category_name NVARCHAR(100) NOT NULL,
        amount FLOAT NOT NULL,
        day_of_month INT NOT NULL
    );
    INSERT INTO #IncomeSeed VALUES (N'משכורת', 18000, 1), (N'קצבה', 2000, 5);

    INSERT INTO Incomes (user_id, category_id, amount, frequency_id, date)
    SELECT @UserId, ic.category_id, i.amount, @MonthlyFrequencyId,
           DATEADD(DAY, i.day_of_month - 1, @MonthStart)
    FROM #IncomeSeed i
    JOIN IncomeCategories ic ON ic.category_name = i.category_name
    WHERE NOT EXISTS (
        SELECT 1 FROM Incomes existing
        WHERE existing.user_id = @UserId AND existing.category_id = ic.category_id
          AND existing.date = DATEADD(DAY, i.day_of_month - 1, @MonthStart)
          AND ABS(existing.amount - i.amount) < 0.01
    );

    CREATE TABLE #ExpenseSeed (
        category_name NVARCHAR(100) NOT NULL,
        amount FLOAT NOT NULL,
        day_of_month INT NOT NULL,
        expense_type_name NVARCHAR(50) NOT NULL
    );
    INSERT INTO #ExpenseSeed VALUES
        (N'שכירות / משכנתא', 4600, 1, N'קבועה'),
        (N'חשבונות חשמל ומים', 420, 4, N'רגילה'),
        (N'חשבונות חשמל ומים', 175, 12, N'רגילה'),
        (N'ארנונה', 420, 1, N'קבועה'),
        (N'מזון וסופרמרקט', 710, 3, N'רגילה'),
        (N'מזון וסופרמרקט', 865, 9, N'רגילה'),
        (N'מזון וסופרמרקט', 625, 16, N'רגילה'),
        (N'חינוך וילדים', 1150, 2, N'רגילה'),
        (N'חינוך וילדים', 650, 8, N'רגילה'),
        (N'רכב ותחבורה', 340, 6, N'רגילה'),
        (N'רכב ותחבורה', 280, 14, N'רגילה'),
        (N'בריאות', 185, 10, N'רגילה'),
        (N'ביגוד והנעלה', 320, 13, N'חד פעמית'),
        (N'בילויים ומסעדות', 245, 7, N'רגילה'),
        (N'בילויים ומסעדות', 205, 15, N'רגילה'),
        (N'צדקה ומעשרות', 600, 5, N'רגילה'),
        (N'חסכונות והשקעות', 900, 1, N'קבועה'),
        (N'תקשורת', 280, 3, N'קבועה'),
        (N'הלוואות', 1300, 1, N'קבועה'),
        (N'מתנות ושמחות', 250, 11, N'חד פעמית'),
        (N'הוצאות שונות', 220, 17, N'רגילה');

    INSERT INTO Expenses (user_id, category_id, amount, expense_type_id, date)
    SELECT @UserId, c.category_id, e.amount, et.expenseTypeId,
           DATEADD(DAY, CASE WHEN e.day_of_month > DAY(GETDATE()) THEN DAY(GETDATE()) ELSE e.day_of_month END - 1, @MonthStart)
    FROM #ExpenseSeed e
    JOIN Categories c ON c.category_name = e.category_name AND c.category_type_id = @ExpenseTypeId
    JOIN ExpenseTypes et ON et.expenseTypeName = e.expense_type_name
    WHERE NOT EXISTS (
        SELECT 1 FROM Expenses existing
        WHERE existing.user_id = @UserId AND existing.category_id = c.category_id
          AND existing.date = DATEADD(DAY, CASE WHEN e.day_of_month > DAY(GETDATE()) THEN DAY(GETDATE()) ELSE e.day_of_month END - 1, @MonthStart)
          AND ABS(existing.amount - e.amount) < 0.01
    );

    -- Seed three months of trend history from real seeded transactions for the current month.
    ;WITH MonthOffsets AS (
        SELECT -2 AS month_offset, CAST(0.94 AS FLOAT) AS factor
        UNION ALL SELECT -1, CAST(0.98 AS FLOAT)
        UNION ALL SELECT 0, CAST(1.00 AS FLOAT)
    ),
    MonthlyValues AS (
        SELECT @UserId AS user_id, e.category_id,
               CONVERT(CHAR(7), DATEADD(MONTH, o.month_offset, @MonthStart), 126) AS month_year,
               SUM(e.amount * o.factor) AS total_amount
        FROM Expenses e
        CROSS JOIN MonthOffsets o
        WHERE e.user_id = @UserId
          AND e.date >= @MonthStart
          AND e.date < DATEADD(MONTH, 1, @MonthStart)
        GROUP BY e.category_id, o.month_offset
    )
    INSERT INTO Monthly_Expenses_Summary (user_id, category_id, month_year, total_amount)
    SELECT m.user_id, m.category_id, m.month_year, m.total_amount
    FROM MonthlyValues m
    WHERE NOT EXISTS (
        SELECT 1 FROM Monthly_Expenses_Summary existing
        WHERE existing.user_id = m.user_id AND existing.category_id = m.category_id
          AND existing.month_year = m.month_year
    );

    IF NOT EXISTS (
        SELECT 1 FROM Savings_Goals WHERE user_id = @UserId AND name = N'כרית ביטחון'
    )
        INSERT INTO Savings_Goals (user_id, category_id, name, current_balance, target_amount, created_at)
        VALUES (@UserId, NULL, N'כרית ביטחון', 8500, 30000, GETDATE());

    IF NOT EXISTS (
        SELECT 1 FROM Savings_Goals WHERE user_id = @UserId AND name = N'חופשה משפחתית'
    )
        INSERT INTO Savings_Goals (user_id, category_id, name, current_balance, target_amount, created_at)
        VALUES (@UserId, NULL, N'חופשה משפחתית', 5000, 12000, GETDATE());

    DECLARE @EmergencyGoalId INT;
    SELECT @EmergencyGoalId = id FROM Savings_Goals WHERE user_id = @UserId AND name = N'כרית ביטחון';

    IF NOT EXISTS (
        SELECT 1 FROM User_Saving_Goal
        WHERE user_id = @UserId AND goal_id = @EmergencyGoalId
          AND year = YEAR(@MonthStart) AND month = MONTH(@MonthStart)
    )
        INSERT INTO User_Saving_Goal (user_id, goal_id, year, month, allocated_amount, applied, created_at, updated_at)
        VALUES (@UserId, @EmergencyGoalId, YEAR(@MonthStart), MONTH(@MonthStart), 1000, 0, GETDATE(), GETDATE());

    COMMIT TRANSACTION;

    SELECT @UserId AS demo_user_id, N'demo@spendwise.local' AS demo_email,
           YEAR(@MonthStart) AS seeded_year, MONTH(@MonthStart) AS seeded_month,
           N'נתוני דמו נוספו בלי למחוק נתונים קיימים.' AS result;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
