# -*- coding: utf-8 -*-
"""חלק ד׳: ארכיטקטורה, מודלים, מחלקות."""

from build_book_docx import H, P, BULLET, CODE, TABLE, MUTED


def architecture(doc):
    H(doc, "ז׳  ארכיטקטורת המערכת", 1, page_break=True)

    H(doc, "ז׳.1  עקרון העל — הפרדה לשכבות", 2)
    P(doc, "המערכת בנויה בארכיטקטורה רב־שכבתית (Layered "
           "Architecture). כל שכבה מכירה רק את השכבה שמתחתיה "
           "ואינה „קופצת” מעליה. עיקרון זה מביא שלושה "
           "יתרונות: ניתוק בין רכיבים, אפשרות לבדוק כל שכבה "
           "בנפרד, ואפשרות להחליף רכיב בלי לפגוע באחרים.")
    CODE(doc, """
┌─────────────────────────────────────────────┐
│              Client — React + TS            │
│         (Material UI, fetch, RTL)           │
└────────────────────┬────────────────────────┘
                     │  HTTP / JSON
┌────────────────────▼────────────────────────┐
│      Controllers — Flask Blueprints         │
│   (auth, budget, budget_plan, expenses…)    │
├─────────────────────────────────────────────┤
│              DTO — Pydantic v2              │
│       (אימות קלט, מבני תשובה)                │
├─────────────────────────────────────────────┤
│          Services — Business Logic          │
│  (FinancialHealth, CutRanking, Allocation,  │
│   BudgetBuilder, Gradual, EarlyWarning…)    │
├─────────────────────────────────────────────┤
│        Repositories — Data Access           │
│        (שאילתות SQLAlchemy מרוכזות)          │
├─────────────────────────────────────────────┤
│           Models — SQLAlchemy ORM           │
│      (declarative_base, מפתחות, קשרים)       │
├─────────────────────────────────────────────┤
│      Database — SQL Server / SQLite         │
└─────────────────────────────────────────────┘
""", caption="תרשים ארכיטקטורה — Top-Down")

    H(doc, "ז׳.2  שכבות המערכת בפירוט", 2)
    TABLE(doc, ["שכבה", "תפקיד", "אחראית על"],
          [["Models", "מיפוי אובייקטי למסד הנתונים",
            "הגדרת טבלאות, עמודות, מפתחות וקשרי גומלין"],
           ["Repositories", "שכבת גישה לנתונים",
            "ריכוז כל שאילתות ה־ORM במקום אחד"],
           ["Services", "לוגיקה עסקית",
            "אלגוריתמים, חישובים, החלטות"],
           ["DTO", "אובייקטי העברת נתונים",
            "אימות קלט ומבנה תשובות"],
           ["Controllers", "שכבת חשיפה",
            "ניתוב בקשות HTTP והחזרת JSON"]],
          widths=[2.8, 4.6, 7.8])

    H(doc, "ז׳.3  היתרון של שכבת ה־Repository", 2)
    P(doc, "בהיעדר שכבת Repository, כל שירות היה כותב "
           "שאילתות בעצמו — דבר המוביל לכפילות קוד "
           "ולקשיים בתחזוקה. המערכת מרכזת את כל השאילתות "
           "בשכבה ייעודית, כך ששינוי בסכמת הנתונים מחייב "
           "עדכון במקום אחד בלבד. שכבות השירותים עובדות "
           "מול ממשקי ה־Repository, ולא מול ה־ORM ישירות.")

    H(doc, "ז׳.4  תרשים מקרי שימוש (Use Case)", 2)
    CODE(doc, """
        ┌──────────────┐
        │   משק בית    │
        └──────┬───────┘
   ┌───────────┼────────────┬──────────────┐
   │           │            │              │
   ▼           ▼            ▼              ▼
 רישום/    הזנת        צפייה        קבלת תוכנית
 התחברות   הכנסות      בתמונת       תקציבית +
           והוצאות     המצב         התראות
   │           │            │              │
   └───────────┴────────────┴──────────────┘
                     │
        ┌────────────▼────────────┐
        │   מנהלת מערכת (admin)   │
        │  ניהול משקי בית ותפקידים │
        └─────────────────────────┘
""")

    H(doc, "ז׳.5  פונקציות עיקריות במערכת", 2)
    TABLE(doc, ["פונקציה", "שירות", "פלט"],
          [["חישוב תקציב נטו", "BudgetService", "total_income, fixed_costs, net_budget"],
           ["פילוח לפי קטגוריה", "BudgetService", "categories[], סה״כ חיוני/לא־חיוני"],
           ["ציון בריאות", "FinancialHealthService", "score 0–100 + הסבר"],
           ["דירוג לקיצוץ", "CutRankingService", "cut_score, recommended_cut_pct"],
           ["גובה הקיצוץ", "CutAllocationService", "total_cut_needed"],
           ["חלוקת הקיצוץ", "CutAllocationService", "allocation[] מדויק"],
           ["בניית תוכנית", "BudgetBuilderService", "budget[] + pain + status"],
           ["תוכנית הדרגתית", "GradualBudgetService", "תוכנית 6 חודשים"],
           ["התראות", "EarlyWarningService", "alerts[] + UPSERT"]],
          widths=[3.4, 4.6, 7.2])


def models_chapter(doc):
    H(doc, "ח׳  מבני נתונים, מודלים וקשרי גומלין", 1, page_break=True)

    P(doc, "שכבת המודלים ממומשת באמצעות SQLAlchemy ORM. כל "
           "טבלה מיוצגת כמחלקת Python, וכל שורה — כאובייקט. "
           "המודלים מאורגנים לפי תחום בתיקיות משנה.")

    H(doc, "ח׳.1  חלוקת המודלים לפי תחום", 2)
    TABLE(doc, ["תיקייה", "תחום", "מודלים עיקריים"],
          [["core/", "ליבה ומשתמשים",
            "Users, Categories, CategoryStandard, "
            "UserCategoryPreference, UserCategoryGoal, SavingsGoal, "
            "SavingsTransaction"],
           ["Finance/", "פיננסים",
            "Expenses, ExpenseType, Incomes, IncomeCategory, "
            "IncomeFrequency, BudgetPlan, FinancialForecasts, ForecastRanges"],
           ["system/", "מערכת וניתוח",
            "MonthlyExpensesSummary, EarlyWarningAlert, SpecialDate, "
            "HolidayCategorySummary, SpecialPeriodSummary, "
            "SpecialExpense, Recommendations, Texts"],
           ["Goals/", "יעדים",
            "Goal, GoalDetail, GoalStatus, GoalType, GoalExpectation"],
           ["lookups/", "טבלאות עזר", "CategoryType"],
           ["reporting/", "דיווחים", "Report, ReportType"],
           ["survey/", "סקרים", "SatisfactionSurvey, SurveyAnswer"]],
          widths=[2.4, 3.2, 9.6])

    H(doc, "ח׳.2  מודלים מרכזיים", 2)

    H(doc, "Users — משקי הבית", 3)
    TABLE(doc, ["שדה", "טיפוס", "תיאור"],
          [["user_id", "PK int", "מזהה ייחודי"],
           ["first_name / last_name", "varchar", "שם פרטי ומשפחה"],
           ["email", "varchar", "כתובת ייחודית (מומרת לאותיות קטנות)"],
           ["password_hash", "varchar", "סיסמה מגובבת — אינה נשמרת כטקסט"],
           ["role", "varchar", "household / admin"],
           ["family_size", "int", "מספר נפשות (1–20)"],
           ["join_date", "datetime", "תאריך הצטרפות"]],
          widths=[4.0, 2.6, 8.6])

    H(doc, "CategoryStandard — תקן החיים לכל קטגוריה", 3)
    P(doc, "זהו אחד המודלים המשפיעים ביותר על המנוע, "
           "משום שהוא מגדיר את „הנורמה” של כל קטגוריה:")
    TABLE(doc, ["שדה", "טיפוס", "השפעה על המנוע"],
          [["amount_per_person", "float", "בסיס לחישוב תקציב התקן לנפש"],
           ["is_essential", "bool", "משפיע על pain (+4) ועל אחוז הקיצוץ"],
           ["is_fixed_cost", "bool", "קיר — pain=10, אחוז קיצוץ 0"],
           ["max_cut_percent", "float", "תקרת הקיצוץ המותרת לקטגוריה"],
           ["rule_description", "text", "הסבר התקן"]],
          widths=[3.8, 2.4, 9.0])
    P(doc, "המערכת מגיעה עם 17 קטגוריות תקן מובנות, ובהן: "
           "שכירות/משכנתא, חשבונות חשמל ומים, ארנונה, מזון "
           "וסופרמרקט, חינוך וילדים, רכב ותחבורה, בריאות, "
           "ביגוד והנעלה, בילויים ומסעדות, צדקה ומעשרות, "
           "חסכונות והשקעות, תקשורת, ריהוט וציוד לבית, "
           "חופשות ונופש, הלוואות, מתנות ושמחות והוצאות "
           "שונות. לכל אחת מוגדרים סכום לנפש, חיוניות, "
           "קביעות ותקרת קיצוץ.")

    H(doc, "UserCategoryPreference — העדפות אישיות", 3)
    TABLE(doc, ["שדה", "טיפוס", "תיאור"],
          [["user_id", "FK → Users", "שיוך למשק הבית"],
           ["category_id", "FK → Categories", "שיוך לקטגוריה"],
           ["importance_score", "float 0–100", "עד כמה הקטגוריה חשובה למשתמש"]],
          widths=[3.8, 3.4, 8.0])
    P(doc, "שדה זה מזין את מרכיב ה־low_importance בדירוג "
           "הקיצוץ, ומשפיע ישירות על מידת הכאב: קטגוריה "
           "שחשובה למשתמש „כואבת” לקצץ, גם אם היא אינה "
           "חיונית מבחינה תקנית.")

    H(doc, "UserCategoryGoal — יעד חודשי לקטגוריה", 3)
    CODE(doc, """
target_amount = amount_per_person × family_size
""", caption="יעד מחושב אוטומטית בעת ההרשמה ועדכון גודל המשפחה")
    P(doc, "בעת שינוי מספר הנפשות במשק הבית, המערכת "
           "מחשבת מחדש אוטומטית את יעדי כל הקטגוריות. "
           "דבר זה שומר על עקביות הנתונים בלי התערבות ידנית.")

    H(doc, "Expenses — הוצאות", 3)
    TABLE(doc, ["שדה", "טיפוס", "תיאור"],
          [["transaction_id", "PK int", "מזהה התנועה"],
           ["user_id", "FK → Users", "בעל ההוצאה"],
           ["category_id", "FK → Categories", "קטגוריית ההוצאה"],
           ["amount", "float", "סכום"],
           ["date", "date", "תאריך ההוצאה"],
           ["description", "varchar", "תיאור חופשי"]],
          widths=[3.8, 3.0, 8.4])

    H(doc, "MonthlyExpensesSummary — סיכום חודשי", 3)
    P(doc, "טבלה זו היא עמוד השדרה של הניתוח ההתנהגותי. "
           "במקום לחשב מחדש בכל פעם סכומים מטבלת ההוצאות "
           "הגולמית, נשמר כאן סיכום לכל צירוף של משק בית, "
           "קטגוריה וחודש:")
    TABLE(doc, ["שדה", "טיפוס", "תיאור"],
          [["user_id", "FK → Users", "משק הבית"],
           ["category_id", "FK → Categories", "הקטגוריה"],
           ["month_year", "varchar YYYY-MM", "החודש"],
           ["total_amount", "float", "סך ההוצאה באותה קטגוריה באותו חודש"]],
          widths=[3.8, 3.6, 7.8])

    H(doc, "BudgetPlan — תוכנית תקציבית שמורה", 3)
    TABLE(doc, ["שדה", "טיפוס", "תיאור"],
          [["plan_id", "PK int", "מזהה"],
           ["user_id", "FK → Users", "משק הבית"],
           ["category_id", "FK → Categories", "הקטגוריה"],
           ["year / month", "int", "חודש היעד"],
           ["planned_amount", "float", "התקציב המתוכנן"],
           ["created_at", "datetime", "מועד ההפקה"]],
          widths=[3.4, 3.0, 8.8])
    P(doc, "שמירת התוכנית ב־DB מאפשרת השוואה בדיעבד בין "
           "התכנון לביצוע — וזהו הבסיס למערכת ההתראות "
           "המוקדמות ולמעקב אחר עמידה בתוכנית.")

    H(doc, "EarlyWarningAlert — התראות", 3)
    TABLE(doc, ["שדה", "טיפוס", "תיאור"],
          [["alert_id", "PK int", "מזהה"],
           ["user_id", "FK → Users", "משק הבית"],
           ["category_id", "FK, nullable", "NULL = התראה כללית"],
           ["year / month", "int", "החודש"],
           ["alert_type", "varchar(30)", "OVERSPENT / DANGEROUS_TREND / SINGLE_SPIKE"],
           ["severity", "varchar(10)", "HIGH / MEDIUM / LOW"],
           ["budget_amount", "float", "התקציב המתוכנן"],
           ["spent_so_far", "float", "ביצוע עד כה"],
           ["status", "varchar(20)", "ACTIVE / RESOLVED / DISMISSED"],
           ["created_at / resolved_at", "datetime", "זמנים"]],
          widths=[3.8, 3.0, 8.4])

    H(doc, "SpecialDate / HolidayCategorySummary — תקופות מיוחדות", 3)
    TABLE(doc, ["מודל", "שדות עיקריים", "תפקיד"],
          [["SpecialDate", "type_id, start_date, end_date, holiday_name",
            "הגדרת תקופת חג ותחומה"],
           ["HolidayCategorySummary", "special_period_id, category_id, change_ratio",
            "יחס ההשפעה של החג על כל קטגוריה"]],
          widths=[4.4, 6.2, 4.6])

    H(doc, "ח׳.3  תרשים קשרי גומלין", 2)
    CODE(doc, """
                      ┌──────────┐
                      │  Users   │
                      └────┬─────┘
        ┌──────────────┬───┴────┬──────────────┐
        ▼              ▼        ▼              ▼
 ┌─────────────┐ ┌─────────┐ ┌──────────┐ ┌────────────┐
 │Expenses     │ │Incomes  │ │Budget_   │ │EarlyWarning│
 │             │ │         │ │Plans     │ │_Alerts     │
 └──────┬──────┘ └─────────┘ └────┬─────┘ └─────┬──────┘
        │                         │             │
        ▼                         ▼             ▼
 ┌────────────────┐        ┌───────────────────────────┐
 │  Categories    │◄───────┤  Category_Standards       │
 └───────┬────────┘        └───────────────────────────┘
         │
    ┌────┴─────────────────────┬───────────────┐
    ▼                          ▼               ▼
┌───────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ User_Category_    │ │ User_Category_   │ │ Monthly_Expenses │
│ Preferences       │ │ Goals            │ │ _Summary         │
└───────────────────┘ └──────────────────┘ └──────────────────┘

    ┌──────────────┐        ┌─────────────────────────┐
    │Special_Dates │◄───────┤Holiday_Category_Summary │
    └──────────────┘        └─────────────────────────┘
""", caption="קשרי גומלין בין הטבלאות המרכזיות")

    H(doc, "ח׳.4  אסטרטגיית המפתחות", 2)
    BULLET(doc, "כל טבלה מרכזית מחזיקה מפתח ראשי "
                "אוטומטי (PK, autoincrement).",
           bold_prefix="מפתח ראשי — ")
    BULLET(doc, "השיוך למשק הבית מתבצע דרך user_id "
                "בכל טבלה רלוונטית — בדרך זו נשמרת "
                "הפרדה מלאה בין משקי בית.",
           bold_prefix="מפתח זר — ")
    BULLET(doc, "צירוף של user_id + category_id + month_year "
                "משמש כמזהה לוגי בטבלת הסיכום החודשי.",
           bold_prefix="מזהה מורכב — ")

    H(doc, "ח׳.5  ניידות מסד הנתונים", 2)
    P(doc, "חיבור מסד הנתונים מרוכז בקובץ אחד, ומחרוזת "
           "החיבור נקבעת כך:")
    CODE(doc, """
connection_string = os.environ.get("SPENDWISE_DATABASE_URL") or (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    f"?driver={DRIVER.replace(' ', '+')}"
    f"&trusted_connection=yes"
)
""", caption="db_connection.py — בחירת מנוע המסד")
    P(doc, "מכיוון שכל שכבת הגישה לנתונים מבוססת SQLAlchemy, "
           "החלפת מנוע המסד — מ־SQL Server ל־SQLite או "
           "להפך — מתבצעת על־ידי שינוי מחרוזת החיבור בלבד, "
           "ללא נגיעה ולו בשורת קוד אחת בשכבות השירותים "
           "או הראוטרים. תכונה זו נוצלה בפועל: הסביבה "
           "המקומית מריצה SQLite לצורכי פיתוח ובדיקות, "
           "בעוד היעד בפריסה הוא SQL Server.")
