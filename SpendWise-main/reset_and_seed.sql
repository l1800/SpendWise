-- ============================================================================
-- הוספת נתוני דמה (בלי מחיקה) — smart_Encomy
-- הרצה: sqlcmd -S D403-013 -d smart_Encomy -E -i reset_and_seed.sql
-- ============================================================================

-- ===== 1. Category_Types (רק אם לא קיימים) =====
IF NOT EXISTS (SELECT 1 FROM Category_Types WHERE category_type_name = 'income')
    INSERT INTO Category_Types (category_type_name) VALUES ('income');
IF NOT EXISTS (SELECT 1 FROM Category_Types WHERE category_type_name = 'expense')
    INSERT INTO Category_Types (category_type_name) VALUES ('expense');

-- ===== 2. Categories =====
-- מוחק קודם קטגוריות חדשות (3–21) אם קיימות מטעויות קודמות
ALTER TABLE Categories NOCHECK CONSTRAINT ALL;
DELETE FROM Categories WHERE category_id >= 3 AND category_id <= 21;
ALTER TABLE Categories WITH CHECK CHECK CONSTRAINT ALL;

INSERT INTO Categories (category_name, category_type_id, category_description) VALUES
(N'שכירות / משכנתא',        1, N'תשלום דיור חודשי'),
(N'חשבונות חשמל ומים',      1, N'חשבונות שוטפים'),
(N'ארנונה',                 1, N'מס עירוני'),
(N'מזון וסופרמרקט',         1, N'קניות מזון'),
(N'חינוך וילדים',           1, N'תשלומי בית ספר, חוגים, צהרון'),
(N'רכב ותחבורה',            1, N'דלק, תיקונים, טסט'),
(N'בריאות',                 1, N'רופאים, תרופות, ביטוח בריאות'),
(N'ביגוד והנעלה',           1, N'בגדים ונעליים'),
(N'בילויים ומסעדות',        1, N'אוכל בחוץ ופנאי'),
(N'צדקה ומעשרות',           1, N'תרומות'),
(N'חסכונות והשקעות',        1, N'חסכונות עתידיים'),
(N'תקשורת',                 1, N'אינטרנט, טלפון, סלולרי'),
(N'ריהוט וציוד לבית',       1, N'רהיטים ומכשירי חשמל'),
(N'חופשות ונופש',           1, N'חופשות משפחתיות'),
(N'הלוואות',                1, N'החזרי הלוואות'),
(N'מתנות ושמחות',           1, N'מתנות לחתונות ובריתות'),
(N'הוצאות שונות',           1, N'כללי');

INSERT INTO Categories (category_name, category_type_id, category_description) VALUES
(N'משכורת',                 2, N'הכנסה חודשית מעבודה'),
(N'הכנסה מעסק',             2, N'הכנסה מעסק עצמאי'),
(N'קצבאות',                 2, N'קצבאות ביטוח לאומי'),
(N'הכנסות אחרות',           2, N'הכנסות שונות');

-- ===== 3. Category_Standards =====
DELETE FROM Category_Standards WHERE category_id >= 3 AND category_id <= 21;

INSERT INTO Category_Standards (category_id, amount_per_person, is_essential, is_fixed_cost, rule_description, max_cut_percent) VALUES
(3,  800,  1, 1, N'שכירות — חובה קבועה',          0),
(4,  150,  1, 0, N'חשבונות — חיוני, אפשר להתייעל', 20),
(5,  100,  1, 1, N'ארנונה — חובה קבועה',          0),
(6,  400,  1, 0, N'מזון — חיוני, אפשר לצמצם',      15),
(7,  350,  1, 0, N'חינוך — חיוני',                10),
(8,  200,  0, 0, N'רכב — לא חיוני',               30),
(9,  150,  1, 0, N'בריאות — חיוני',               5),
(10, 100,  0, 0, N'ביגוד — לא חיוני',             50),
(11, 120,  0, 0, N'בילויים — מותרות',             70),
(12, 200,  0, 0, N'צדקה — חשוב אבל גמיש',          30),
(13, 150,  0, 0, N'חסכונות — גמיש',               50),
(14, 80,   1, 0, N'תקשורת — חיוני, אפשר להתייעל',  20),
(15, 80,   0, 0, N'ריהוט — לא חיוני',             60),
(16, 100,  0, 0, N'חופשות — מותרות',              80),
(17, 300,  1, 1, N'הלוואות — חובה קבועה',         0),
(18, 60,   0, 0, N'מתנות — גמיש',                 50),
(19, 100,  0, 0, N'הוצאות שונות — גמיש',          40);

-- ===== 4. ExpenseType =====
IF NOT EXISTS (SELECT 1 FROM ExpenseType WHERE expense_type_name = N'רגילה')
    INSERT INTO ExpenseType (expense_type_name) VALUES (N'רגילה'), (N'קבועה'), (N'חד פעמית'), (N'חירום');

-- ===== 5. IncomeCategories =====
IF NOT EXISTS (SELECT 1 FROM IncomeCategories WHERE category_name = N'משכורת')
    INSERT INTO IncomeCategories (category_name) VALUES (N'משכורת'), (N'עסק'), (N'קצבה'), (N'אחר');

-- ===== 6. Income_Frequency =====
IF NOT EXISTS (SELECT 1 FROM Income_Frequency WHERE frequency_name = N'חודשי')
    INSERT INTO Income_Frequency (frequency_name) VALUES (N'חודשי'), (N'חד פעמי'), (N'רבעוני'), (N'שנתי');

-- ===== 7. User_Category_Preferences (user_id=9 = Gitty Weiss) =====
DELETE FROM User_Category_Preferences WHERE user_id = 9;

INSERT INTO User_Category_Preferences (user_id, category_id, importance_score) VALUES
(9, 3,  100), (9, 4,  80), (9, 5,  90), (9, 6,  70), (9, 7,  85),
(9, 8,  50),  (9, 9,  95), (9, 10, 30), (9, 11, 20), (9, 12, 60),
(9, 13, 40),  (9, 14, 75), (9, 15, 25), (9, 16, 15), (9, 17, 100),
(9, 18, 35),  (9, 19, 45);

-- ===== 8. User_Category_Goal =====
DELETE FROM User_Category_Goal WHERE user_id = 9;

INSERT INTO User_Category_Goal (user_id, category_id, target_amount) VALUES
(9, 3,  4000), (9, 4,  750),  (9, 5,  500),  (9, 6,  2000), (9, 7,  1750),
(9, 8,  1000), (9, 9,  750),  (9, 10, 500),  (9, 11, 600),  (9, 12, 1000),
(9, 13, 750),  (9, 14, 400),  (9, 15, 400),  (9, 16, 500),  (9, 17, 1500),
(9, 18, 300),  (9, 19, 500);

-- ===== 9. User_Saving_Goal =====
DELETE FROM User_Saving_Goal WHERE user_id = 9;

INSERT INTO User_Saving_Goal (user_id, saving_mode, target_percent, target_amount)
VALUES (9, 'MEDIUM', 8, NULL);

-- ===== 10. Incomes =====
DELETE FROM Incomes WHERE user_id = 9 AND date >= '2026-07-01';

INSERT INTO Incomes (user_id, category_id, amount, frequency_id, date) VALUES
(9, 20, 12000, 1, '2026-07-01'),
(9, 23, 1500,  1, '2026-07-05');

-- ===== 11. Expenses =====
DELETE FROM Expenses WHERE user_id = 9 AND date >= '2026-07-01';

INSERT INTO Expenses (user_id, category_id, amount, expense_type_id, date) VALUES
(9, 3,  4000, 2, '2026-07-01'),
(9, 4,  680,  1, '2026-07-03'),
(9, 5,  500,  2, '2026-07-01'),
(9, 6,  2200, 1, '2026-07-07'),
(9, 7,  1600, 1, '2026-07-02'),
(9, 8,  450,  1, '2026-07-10'),
(9, 9,  300,  1, '2026-07-08'),
(9, 10, 350,  1, '2026-07-12'),
(9, 11, 500,  1, '2026-07-13'),
(9, 12, 800,  1, '2026-07-05'),
(9, 13, 500,  1, '2026-07-01'),
(9, 14, 350,  1, '2026-07-03'),
(9, 17, 1500, 2, '2026-07-01'),
(9, 19, 200,  1, '2026-07-11');

-- ===== 12. Monthly_Expenses_Summary =====
DELETE FROM Monthly_Expenses_Summary WHERE user_id = 9 AND month_year IN ('2026-05', '2026-06', '2026-07');

INSERT INTO Monthly_Expenses_Summary (user_id, category_id, month_year, total_amount) VALUES
(9,3,'2026-07',4000),(9,4,'2026-07',680),(9,5,'2026-07',500),
(9,6,'2026-07',2200),(9,7,'2026-07',1600),(9,8,'2026-07',450),
(9,9,'2026-07',300),(9,10,'2026-07',350),(9,11,'2026-07',500),
(9,12,'2026-07',800),(9,13,'2026-07',500),(9,14,'2026-07',350),
(9,17,'2026-07',1500),(9,19,'2026-07',200),
(9,3,'2026-06',4000),(9,4,'2026-06',700),(9,5,'2026-06',500),
(9,6,'2026-06',2400),(9,7,'2026-06',1550),(9,8,'2026-06',380),
(9,9,'2026-06',200),(9,10,'2026-06',280),(9,11,'2026-06',650),
(9,12,'2026-06',800),(9,13,'2026-06',500),(9,14,'2026-06',350),
(9,17,'2026-06',1500),(9,19,'2026-06',150),
(9,3,'2026-05',4000),(9,4,'2026-05',650),(9,5,'2026-05',500),
(9,6,'2026-05',2100),(9,7,'2026-05',1600),(9,8,'2026-05',520),
(9,9,'2026-05',350),(9,10,'2026-05',400),(9,11,'2026-05',550),
(9,12,'2026-05',800),(9,13,'2026-05',500),(9,14,'2026-05',350),
(9,17,'2026-05',1500),(9,19,'2026-05',300);

PRINT N'Done!';
