# פרויקט כלכלה נבונה — תיעוד מלא

> **מטרה:** מערכת חכמה לניהול כלכלת הבית — ניתוח מצב פיננסי, דירוג קטגוריות לקיצוץ, בניית תקציב חודשי והפקת המלצות.
>
> **משתמשים:** חרדי, צוות פיתוח Gitty
>
> **DB:** SQL Server — `smart_Encomy`
>
> **עדכון אחרון:** יולי 2026

---

## 📁 מבנה הפרויקט

```
פרויקט כלכלה נבונה/
├── main.py                  # Flask app + בדיקות הרצה (test_allocate_edge_cases)
├── db_connection.py          # חיבור SQLAlchemy ל-SQL Server
├── models/                   # SQLAlchemy ORM Models
│   ├── base.py               # Base = declarative_base()
│   ├── import_all.py         # טוען את כל המודלים (לפני create_all)
│   ├── core/                 # Users, Categories, CategoryStandard, UserCategoryPreference, UserSavingGoal, UserCategoryGoal
│   ├── Finance/              # Expenses, ExpenseType, Incomes, IncomeCategory, IncomeFrequency, FinancialForecasts, ForecastRanges
│   ├── system/               # MonthlyExpensesSummary, SpecialPeriodSummary, HolidayCategorySummary, SpecialDate, SpecialDateType, SpecialExpense, Recommendations, Texts, EarlyWarningAlert
│   ├── Goals/                # Goals, GoalDetails, GoalStatus, GoalTypes, GoalsExpectations
│   ├── lookups/              # CategoryType
│   ├── reporting/            # Reports, ReportTypes
│   ├── survey/               # SatisfactionSurvey, SurveyAnswers
│   └── system/               # MonthlyExpensesSummary, SpecialPeriodSummary, HolidayCategorySummary, SpecialDate, SpecialDateType, SpecialExpense, Recommendations, Texts
├── repositories/             # Data access layer (SQLAlchemy queries)
│   ├── base_repository.py    # BaseRepository — add/delete
│   ├── core/                 # Categories, CategoryStandard, UserCategoryPreference, UserSavingGoal, UserCategoryGoal, Users
│   ├── Finance/              # BudgetRepository, FinancialRepository, Expenses, ExpenseTypes, Incomes, IncomeCategories, IncomeFrequency, FinancialForecasts, ForecastRanges
│   ├── Goals/                # Goals, GoalDetails, GoalStatus, GoalTypes
│   ├── lookups/              # CategoryTypes
│   ├── reporting/            # Reports, ReportTypes
│   ├── survey/               # SatisfactionSurvey, SurveyAnswers
│   └── system/               # MonthlyExpensesSummary, SpecialPeriodSummary, HolidayCategorySummary, SpecialDates, SpecialDateTypes, SpecialExpenses, Recommendations, Texts, EarlyWarningAlert
├── services/                 # Business logic layer
│   ├── core/                 # UserCategoryPreferenceService, UserSavingGoalService, UserCategoryGoalService, Categories, CategoryStandard, Users
│   ├── Finance/              # ⭐ הקבצים הכי חשובים:
│   │   ├── budget_service.py            # BudgetService — תקציב נטו, הוצאות לפי קטגוריה, תקציב סטנדרטי, גירעון חודש קודם
│   │   ├── FinancialService.py          # FinancialService — לחץ פיננסי בסיסי (ratio-based)
│   │   ├── FinancialHealthService.py    # ⭐ FinancialHealthService — ציון משולב: spike + behavior + budget
│   │   ├── FinancialStressService.py    # FinancialStressService — חישוב קפיצות חריגות (spike)
│   │   ├── BehaviorStressService.py     # BehaviorStressService — ניתוח מגמות התנהגותיות
│   │   ├── CategoryBehaviorService.py   # CategoryBehaviorService — ציון התנהגות לקטגוריה בודדת
│   │   ├── CutRankingService.py         # ⭐ CutRankingService — שלב 9: דירוג קטגוריות לקיצוץ (אחוזים בלבד)
│   │   ├── CutAllocationService.py      # ⭐ CutAllocationService — שלב 10: חישוב סכום קיצוץ + חלוקה בפועל
│   │   ├── Expenses.py, ExpenseTypes.py, Incomes.py, IncomeCategories.py, IncomeFrequency.py, FinancialForecasts.py, ForecastRanges.py
│   └── system/               # MonthlyExpensesSummary, SpecialPeriodSummary, HolidayCategorySummary, SpecialDates, SpecialDateTypes, SpecialExpenses, Recommendations, Texts, EarlyWarningAlert
├── controller/               # Flask Blueprint routes
│   ├── core/                 # categories, users, CategoryStandard, UserCategoryGoal, UserCategoryPreference, UserSavingGoal
│   ├── Finance/              # budget_controller, CutAllocation, financial_controller, Expenses, ExpenseTypes, FinancialForecasts, ForecastRanges, IncomeCategories, IncomeFrequency, Incomes
│   ├── Goals/                # Goals, GoalDetails
│   ├── lookups/              # CategoryTypes
│   ├── reporting/            # Reports, ReportTypes
│   ├── survey/               # SatisfactionSurvey, SurveyAnswers
│   └── system/               # HolidayCategorySummary, SpecialPeriodSummary, SpecialDates, MonthlyExpensesSummary
├── dto/                      # Data Transfer Objects (create/response schemas)
│   └── ... (מקביל ל-controller)
├── client/                   # Frontend React/TypeScript (⚠️ כרגע לא מחובר — פרויקט ספרייה לדוגמה)
│   ├── src/components/       # login, signUp, home, header, allBook, addBook, lend, admin, oneBook, loading
│   └── src/server/           # API calls — book.ts, comment.ts, lend.ts, users.ts
└── venv/                     # Python venv
```

---

## 🔗 איך הקבצים מתחברים — Flow ראשי

### Pipeline ההמלצות (שלבים 1–10, מה שכבר קיים):

```
1. BudgetService.calculate_net_budget(user_id, year, month)
   └─> BudgetRepository.get_incomes_by_month() + get_fixed_costs_by_month()
   └─> מחזיר: total_income, fixed_costs, net_budget

2. BudgetService.get_monthly_expenses_by_category(user_id, year, month)
   └─> BudgetRepository.get_monthly_expenses_by_category()
   └─> מחזיר: categories[], essential_total, non_essential_total

3. BudgetService.get_standard_budget(family_size)
   └─> BudgetRepository.get_category_standards()
   └─> מחזיר: standards[] (לפי נפש)

4–7. הערכת לחץ פיננסי:
   FinancialHealthService.calculate_financial_score(user_id, year, month)
   ├─> FinancialStressService.calculate_spike_stress()     [20% משקל — חריגות]
   ├─> BehaviorStressService.calculate_behavior_stress()    [50% משקל — מגמות]
   └─> FinancialRepository.get_financial_pressure()         [30% משקל — לחץ תקציבי]
   └─> מחזיר: score (0–100), status, explanation, smart_explanation

8. UserCategoryPreferenceService.get_preferences_map(user_id)
   └─> מחזיר: {category_id: importance_score}

9. CutRankingService.rank_categories(user_id, year, month)
   ├─> BudgetService.get_monthly_expenses_by_category()  → שלב 2
   ├─> UserCategoryPreferenceRepository.get_by_user()    → שלב 8
   ├─> CategoryStandardRepository.get_all()              → is_essential, is_fixed_cost
   └─> MonthlyExpensesSummaryService.calculate_category_analysis() → מגמות
   └─> מחזיר: ranking[] (cut_score, recommended_cut_pct, current_amount, reason)

10. CutAllocationService:
    calculate_total_cut_needed(ranking, net_budget, stress_score, user_id, family_size, year, month)
    ├─> BudgetService.get_previous_month_deficit()        → deficit_part
    ├─> stress_score × base_budget × multiplier           → stress_part
    └─> CategoryStandardRepository.get_all() × family_size → standard_pressure
    └─> מחזיר: total_cut_needed (מעוגל)
    └─> חיסכון = מה שנשאר בסוף החודש, לא חלק מהנוסחה

    allocate_cuts(ranking, total_cut)
    └─> מפזר את הקיצוץ לפי recommended_cut_pct + max_pct
    └─> עושה scaling + redistribution
    └─> מחזיר: total_cut_needed, actual_cut, remaining_to_cut, allocation[]
```

---

## 📊 סטטוס מפורט של כל שלב

### 🔵 שלב 1: הבנת מצב פיננסי בסיסי

| # | פונקציונליות | קובץ/שירות | סטטוס |
|---|-------------|------------|--------|
| 1 | חישוב כסף פנוי חודשי | `BudgetService.calculate_net_budget()` | ✅ גמור |
| 2 | טעינת הוצאות לפי קטגוריות | `BudgetService.get_monthly_expenses_by_category()` | ✅ גמור |
| 3 | חישוב תקציב סטנדרטי לפי אדם | `BudgetService.get_standard_budget()` | ✅ גמור |

### 🔵 שלב 2: ניתוח פיננסי

| # | פונקציונליות | קובץ/שירות | סטטוס |
|---|-------------|------------|--------|
| 4 | חישוב רמת לחץ פיננסי | `FinancialHealthService.calculate_financial_score()` | ✅ גמור |
| 5 | ניתוח מגמות לאורך זמן | `MonthlyExpensesSummaryService.calculate_category_analysis()` | ✅ גמור |
| 6 | זיהוי קפיצות חריגות | `FinancialStressService.calculate_spike_stress()` | ✅ גמור |

### 🔵 שלב 3: התאמה אישית למשתמש

| # | פונקציונליות | קובץ/שירות | סטטוס |
|---|-------------|------------|--------|
| 7 | חשיבות אישית לכל קטגוריה | `UserCategoryPreferenceService` | ✅ גמור |
| 8 | הפרדה בין חובה לגמיש | דרך `CategoryStandard.is_essential`, `is_fixed_cost` | ✅ גמור |

### 🔵 שלב 4: קבלת החלטות

| # | פונקציונליות | קובץ/שירות | סטטוס |
|---|-------------|------------|--------|
| 9 | דירוג קטגוריות לקיצוץ | `CutRankingService.rank_categories()` | ✅ גמור |
| 10 | חישוב סכום קיצוץ נדרש + חלוקה | `CutAllocationService.calculate_total_cut_needed()` + `allocate_cuts()` | ✅ גמור |
| 11 | **בניית תקציב חדש לחודש הבא** | `BudgetPlanService.build_plan()` → `BudgetBuilderService` | ✅ גמור |

### 🔵 שלב 5: המלצות למשתמש

| # | פונקציונליות | קובץ/שירות | סטטוס |
|---|-------------|------------|--------|
| 12 | יצירת המלצות טקסט | `FinancialHealthService.build_explanation()` | 🟡 בסיסי |
| 13 | הסבר חכם V1 | `build_smart_explanation()` | ✅ גמור |
| 14 | הסבר חכם V2 | `build_smart_explanation_v2()` | 🟡 קיים, ריק |

### 🔵 שלב 6: מערכות מתקדמות

| # | פונקציונליות | סטטוס |
|---|-------------|--------|
| 15 | חיזוי מינוס עתידי | ❌ לא קיים |
| 16 | Early Warning System | ✅ גמור — `EarlyWarningService` + `check_spending_vs_budget()` |
| 17 | **שמירת תוכנית תקציבית ב-DB** | ✅ גמור — `Budget_Plans` table |
| 18 | **API למצב ביצוע תקציב** | ✅ גמור — `GET /budget/status?user_id=&year=&month=` |
| 19 | Cash Flow יומי | ❌ לא קיים |
| 20 | יכולת הישרדות כלכלית | ❌ לא קיים |

---

## ⚠️ בעיות ידועות

### `main.py`
- הקובץ במצב "בדיקות" — מכיל המון `import` כפולים ו־`test_allocate_edge_cases()` שרץ ב־`__main__`
- ה-Flask app (החלק העליון) מושבת בהערה
- צריך לנקות ולסדר מחדש

### `CutAllocation.py` (controller)
- הקוד לא תואם לחתימה האמיתית של `calculate_total_cut_needed` — חסרים פרמטרים (`family_size`, `year`, `month`)
- `CutAllocationService.__init__` מקבל 3 פרמטרים אבל ב-controller מועברים רק 2 (budget_service)

### Frontend
- `client/` מכיל פרויקט React של ספרייה — לא קשור עדיין לפרויקט הכלכלה
- `client/fronted/` (שגיאת כתיב) — נראה כמו העתק/ניסיון

### מודל `Monthly_Expenses_Summary`
- הקובץ `Monthly_Expenses_Summary.py` ב-controller וב-DTO סומנו כ-Deleted ב-git status

### `CategoryBehaviorService`
- מייבא את עצמו פעמיים (`BehaviorStressService.py:1-2`)

---

## 🧭 צעד מומלץ הבא (שלב 11)

**בניית תקציב חדש לחודש הבא:**
- פונקציה שלוקחת:
  - `allocation[]` מתוך `allocate_cuts()` (כמה לקצץ בכל קטגוריה)
  - `net_budget` (הכנסות פחות קבועות)
  - `total_cut_needed`
- ומחזירה:
  - **תקציב מתוכנן** לכל קטגוריה לחודש הבא
  - **סכום חודשי מותר** (net_budget - total_cut)
  - **השוואה** מול חודש נוכחי (כמה חסכנו)
  - **התראות** על קטגוריות שדורשות תשומת לב

---

## 📝 אופן עבודה עם Claude Code

- **אין להוסיף קוד ללא אישור** — קודם הצעה, אחרי אישור ביצוע
- **בדיקות** — להריץ אחרי כל שינוי
- **קומיטים** — רק כשהמשתמש מבקש

---

## 🔑 מודלים מרכזיים — שדות חשובים

### `CategoryStandard` (`Category_Standards`)
קובע את ה"נורמה" לכל קטגוריה:
- `amount_per_person` — תקציב מומלץ לנפש
- `is_essential` — חיוני / רצון
- `is_fixed_cost` — קבוע (שכ"ד) או גמיש
- `max_cut_percent` — כמה אחוז מקסימום אפשר לקצץ (default 100)

### `UserCategoryPreference` (`User_Category_Preferences`)
העדפות אישיות של המשתמש:
- `importance_score` — 0 עד 100, כמה הקטגוריה חשובה למשתמש

### `SavingsGoal` (`Savings_Goals`)
יעדי חיסכון — המשתמש מגדיר לכמה דברים הוא חוסך:
- `name` — "דירה", "חופשה", "ריהוט", "חירום"
- `current_balance` — יתרה נוכחית
- `target_amount` — יעד אופציונלי

### `SavingsTransaction` (`Savings_Transactions`)
תנועות בחיסכון:
- `amount` — חיובי=הפקדה, שלילי=משיכה
- API: `POST /savings/goals` — יצירת יעד
- API: `POST /savings/one-time-expense` — הוצאה חד-פעמית (מושכת מחיסכון)

> `User_Saving_Goal` הוסר — חיסכון = מה שנשאר בסוף החודש, לא נקבע מראש.

### `UserCategoryGoal` (`User_Category_Goal`)
יעד חודשי אידיאלי לכל קטגוריה — מחושב אוטומטית:
- `target_amount` = `amount_per_person` (מתוך `Category_Standards`) × `family_size` (מתוך `Users`)
- API: `POST /user_goal/user/<id>/recalculate` — מחשב מחדש
- API: `GET /user_goal/user/<id>/targets` — מחזיר `{category_id: target_amount}`

### `MonthlyExpensesSummary` (`Monthly_Expenses_Summary`)
סיכום חודשי — הבסיס לניתוח מגמות:
- `user_id`, `category_id`, `month_year` (YYYY-MM), `total_amount`

---

## 🚨 Early Warning System (שלב 16) — 🟡 מתוכנן

### טבלה: `EarlyWarning_Alerts`
| שדה | טיפוס | הערה |
|---|---|---|
| alert_id | PK int | autoincrement |
| user_id | FK→Users | |
| category_id | FK→Categories, nullable | NULL=כללי |
| year, month | int | חודש ההתראה |
| alert_type | varchar(30) | OVERSPENT / DANGEROUS_TREND / SINGLE_SPIKE |
| severity | varchar(10) | HIGH / MEDIUM / LOW |
| title | varchar(200) | |
| message | text | |
| budget_amount | float | תקציב מתוכנן |
| spent_so_far | float | ביצוע עד כה |
| status | varchar(20) | ACTIVE / RESOLVED / DISMISSED |
| created_at | datetime | |
| resolved_at | datetime, nullable | |

### לוגיקה
- **check_spending_vs_budget(plan)**: משווה הוצאות בפועל (שאילתה ל-Expenses) מול תקציב מתוכנן (מתוך allocation). בודק: (א) חריגה כללית — budget_used_pct vs days_elapsed_pct (ב) חריגה לפי קטגוריה — spent vs planned. עושה UPSERT (לא כפילות), ו-RESOLVE לקטגוריות שחזרו לתקין.
- **check_single_expense(amount, category_id)**: בזמן הכנסת הוצאה — בודק האם חריגה מול ממוצע עבר (Monthly_Expenses_Summary). אם amount > avg×2 → SINGLE_SPIKE.

### קבצים
| # | קובץ | פעולה |
|---|---|---|
| 1 | `models/system/EarlyWarningAlert.py` | חדש — Model |
| 2 | `repositories/system/EarlyWarningAlert.py` | חדש — CRUD + get_existing_alert + resolve/dismiss |
| 3 | `services/Finance/EarlyWarningService.py` | חדש — check_spending_vs_budget + check_single_expense + helpers |
| 4 | `dto/system/EarlyWarningAlertDto.py` | חדש — CreateDto, ResponseDto, CheckResponseDto |
| 5 | `controller/Finance/EarlyWarning.py` | חדש — GET alerts, PUT dismiss |
| 6 | `models/core/Users.py` | עדכון — +relationship early_warning_alerts |
| 7 | `models/core/Categories.py` | עדכון — +relationship early_warning_alerts |
| 8 | `models/import_all.py` | עדכון — +import |
| 9 | `services/Finance/BudgetPlanService.py` | עדכון — +early_warning_service בפרמטרים, +שלב 8 בקריאה |

### Holiday Adjustment (שלב 5.5)

**לוגיקה:** בזמן בניית תקציב חודשי, בודק האם יש תקופת חג ב-`Special_Dates` שחופפת לחודש היעד. אם כן, שולף מ-`Holiday_Category_Summary` את `change_ratio` לכל קטגוריה ומגדיל את `planned_amount` בהתאם. קטגוריות שלא מופיעות בטבלת החגים — לא משתנות.

**טבלאות:**
- `Special_Dates` — type_id, start_date, end_date, holiday_name
- `Holiday_Category_Summary` — special_period_id (= type_id), category_id, change_ratio

**קבצים:**
| # | קובץ | פעולה |
|---|---|---|
| 1 | `services/Finance/HolidayAdjustmentService.py` | חדש — get_holiday_adjustments + adjust_budget_items |
| 2 | `models/Finance/BudgetPlan.py` | עדכון — +holiday_adjustment column |
| 3 | `repositories/Finance/BudgetPlanRepository.py` | עדכון — save holiday_adjustment |
| 4 | `services/Finance/BudgetPlanService.py` | עדכון — STEP 5.5 holiday adjustment |
| 5 | `controller/Finance/budget_plan_controller.py` | עדכון — wire HolidayAdjustmentService |
| 6 | `jobs/monthly_budget_job.py` | עדכון — wire HolidayAdjustmentService |
| 7 | `models/import_all.py` | תיקון — +UserSavingGoal (באג קיים) |

### API — Budget Plan
| Method | Route | תיאור |
|---|---|---|
| GET | `/budget/plan/<user_id>/<year>/<month>` | בונה + שומר תוכנית תקציבית (כולל התאמת חגים) |
| GET | `/budget/status?user_id=&year=&month=` | מצב ביצוע — spent vs planned + EarlyWarning |
| GET | `/budget/plans?user_id=&year=&month=` | צפייה בנתונים גולמיים מ-Budget_Plans |

### API
- `GET /api/early-warning/alerts?user_id=&year=&month=` — התראות לחודש
- `PUT /api/early-warning/alerts/<id>/dismiss` — דחייה

---

## 🔑 Budget_Plans — טבלה חדשה

### טבלה: `Budget_Plans`
| שדה | טיפוס | הערה |
|---|---|---|
| plan_id | PK int | autoincrement |
| user_id | FK→Users | |
| category_id | FK→Categories | |
| year | int | |
| month | int | |
| planned_amount | float | התקציב המתוכנן לקטגוריה |
| created_at | datetime | |

### קבצים
| # | קובץ | סטטוס |
|---|---|---|
| 1 | `models/Finance/BudgetPlan.py` | ✅ Model |
| 2 | `repositories/Finance/BudgetPlanRepository.py` | ✅ save_plan_for_month + get_plan_for_month |
| 3 | `models/import_all.py` | ✅ +import |
| 4 | `models/core/Users.py` | ✅ +relationship budget_plans |
| 5 | `models/core/Categories.py` | ✅ +relationship budget_plans |
| 6 | `services/Finance/BudgetPlanService.py` | ✅ שלב 5.5 — שמירה אוטומטית אחרי build_next_month_budget |

## 🌐 API Endpoints — Budget Plan

| Method | Route | תיאור |
|---|---|---|
| GET | `/budget/plan/<user_id>/<year>/<month>` | בונה (או טוען) תוכנית תקציבית + שומרת ב-DB |
| GET | `/budget/status?user_id=&year=&month=` | מצב ביצוע — spent vs planned לכל קטגוריה + EarlyWarning alerts |

**זרימה:**
1. `GET /budget/plan/1/2026/7` — מייצר תוכנית, שומר ב-Budget_Plans, מחזיר JSON מלא
2. `GET /budget/status?user_id=1` — שולף מ-Budget_Plans + משווה מול Expenses בפועל + EarlyWarning

> 📌 הקוד המלא נמצא בסשן הקודם. המסמך הזה הוא מפת מפתחות — מבנה, לוגיקה, תלויות.

---

> 📌 **הערה:** קובץ זה נכתב כדי לחסוך קריאה מחדש של כל הפרויקט בכל סשן.
> עדכן אותו כשמתווספים שירותים חדשים או משתנה הארכיטקטורה.
