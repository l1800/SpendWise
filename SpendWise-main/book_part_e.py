# -*- coding: utf-8 -*-
"""חלק ה׳: סקירת מחלקות, טכנולוגיות וספריות."""

from build_book_docx import H, P, BULLET, CODE, TABLE, MUTED


def classes(doc):
    H(doc, "ט׳  סקירת המחלקות לפי שכבות", 1, page_break=True)

    H(doc, "ט׳.1  שכבת המודלים (Models)", 2)
    P(doc, "שכבת המודלים מורכבת מ־38 מחלקות, הממופות "
           "לטבלאות במסד הנתונים באמצעות Base של SQLAlchemy. "
           "כל מחלקה מגדירה __tablename__, עמודות ומפתחות, "
           "ולעיתים גם קשרי relationship לטבלאות סמוכות.")
    CODE(doc, """
from sqlalchemy.orm import declarative_base

Base = declarative_base()
""", caption="models/base.py — הבסיס לכל המודלים")
    P(doc, "קובץ import_all.py מרכז את ייבוא כל המודלים "
           "במקום אחד. הדבר הכרחי לפני יצירת הסכמה "
           "(create_all) — בלעדיו SQLAlchemy אינו „מכיר” "
           "את הטבלאות.")

    H(doc, "ט׳.2  שכבת הגישה לנתונים (Repositories)", 2)
    P(doc, "שכבה זו מרכזת את כל שאילתות ה־ORM. כל "
           "Repository מקבל הפעם session של SQLAlchemy "
           "ומספק מתודות קריאה וכתיבה. הבסיס המשותף:")
    CODE(doc, """
class BaseRepository:
    def __init__(self, session):
        self.session = session

    def add(self, entity):
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity):
        self.session.delete(entity)
        self.session.commit()
""", caption="repositories/base_repository.py — מחזור חיים של ישות")
    TABLE(doc, ["Repository", "תפקיד"],
          [["BudgetRepository", "שאילתות ריכוזיות לתקציב: הכנסות, "
                                "הוצאות קבועות, פילוח לפי קטגוריה, גירעון חודש קודם"],
           ["FinancialRepository", "חישוב לחץ פיננסי ביחס להכנסה"],
           ["BudgetPlanRepository", "שמירה ושליפה של תוכניות תקציביות"],
           ["EarlyWarningAlert", "CRUD התראות + get_existing_alert + resolve/dismiss"],
           ["MonthlyExpensesSummary", "סיכומים חודשיים לחישוב מגמות"],
           ["SpecialDates / HolidayCategorySummary", "שליפת תקופות חג ויחסי השפעה"]],
          widths=[5.4, 9.8])

    H(doc, "ט׳.3  שכבת השירותים (Services)", 2)
    P(doc, "זוהי השכבה העשירה במערכת — 47 מחלקות שירות. "
           "כל שירות אחראי על תחום אחד בלבד, וכך נשמר "
           "עיקרון האחריות היחידה.")

    H(doc, "שירותי הליבה הפיננסיים", 3)
    TABLE(doc, ["שירות", "אחריות", "פלט"],
          [["BudgetService", "תקציב נטו, פילוח הוצאות, תקציב תקן, גירעון",
            "net_budget, categories[], standards[]"],
           ["FinancialStressService", "זיהוי קפיצות חריגות",
            "spike_stress 0–100"],
           ["CategoryBehaviorService", "ציון התנהגות לקטגוריה בודדת",
            "score 0–100 (עם soft clamp)"],
           ["BehaviorStressService", "שילוב ציוני ההתנהגות המשוקלל",
            "behavior_stress 0–100"],
           ["FinancialHealthService", "הציון המשולב והסבר אנושי",
            "score, status, explanation"],
           ["CutRankingService", "דירוג קטגוריות לקיצוץ",
            "ranking[] עם cut_score ו־pct"],
           ["CutAllocationService", "יעד הקיצוץ וחלוקתו בפועל",
            "total_cut_needed, allocation[]"],
           ["BudgetBuilderService", "בניית התוכנית החודשית + pain",
            "budget[], status, warnings"],
           ["GradualBudgetService", "תוכנית הדרגתית בת חצי שנה",
            "תוכנית + דוח לפני/אחרי"],
           ["HolidayAdjustmentService", "התאמת תקציב לתקופות חג",
            "planned_amount מעודכן"],
           ["EarlyWarningService", "התראות בזמן אמת",
            "alerts[] + UPSERT"],
           ["RecommendationTextService", "יצירת טקסט ההמלצות",
            "headline, sections[]"]],
          widths=[4.0, 5.6, 5.6])

    H(doc, "BudgetPlanService — המתזמר", 3)
    P(doc, "זהו השירות המרכזי שמחבר את כל שלבי המנוע "
           "לכדי תהליך אחד. הוא מקבל בהרכבה (dependency "
           "injection) את כל השירותים הנדרשים ומריץ את "
           "השלבים בסדר:")
    CODE(doc, """
class BudgetPlanService:
    def __init__(self, budget_service, cut_ranking_service,
                 cut_allocation_service, builder_service,
                 recommendation_service, early_warning_service,
                 budget_plan_repository,
                 financial_health_service=None,
                 user_repository=None):
        ...

    def build_plan(self, user_id, year, month):
        # STEP 1 — Net budget
        net_budget = self.budget_service.calculate_net_budget(...)
        # STEP 2 — Ranking
        ranking_result = self.cut_ranking_service.rank_categories(...)
        # STEP 3 — Total cut (כולל ציון בריאות)
        total_cut = self.cut_allocation_service.calculate_total_cut_needed(...)
        # STEP 4 — Allocation
        allocation = self.cut_allocation_service.allocate_cuts(...)
        # STEP 5 — Build plan
        plan = self.builder_service.build_next_month_budget(...)
        # STEP 5.5 — Save to DB
        self.budget_plan_repository.save_plan_for_month(...)
        # STEP 6 — Text layer
        text = self.recommendation_service.generate(plan)
        # STEP 8 — Early warning
        early_warning = self.early_warning_service.check_spending_vs_budget(...)
        return { "net_budget": ..., "budget": ..., "early_warning": ... }
""", caption="BudgetPlanService.build_plan — שרשרת השלבים")
    P(doc, "תבנית זו — שירות מתזמר המחזיק הפניות "
           "לשירותים אחרים — נקראת Composition Root, "
           "ומאפשרת להרכיב את המערכת בגמישות ובקלות "
           "בבדיקות.")

    H(doc, "HouseholdSetupService — אתחול משק בית", 3)
    P(doc, "בעת הרשמה או התחברות ראשונה, השירות יוצר "
           "אוטומטית את כל מה שנדרש למשק בית חדש: סוגי "
           "קטגוריה (expense/income), 17 קטגוריות ההוצאה "
           "עם התקנים שלהן, קטגוריות הכנסה, סוגי הוצאה, "
           "תדירויות הכנסה, וכן רשומות העדפה ויעד אישיות "
           "לכל קטגוריה. הפעולה אידמפוטנטית — הרצה חוזרת "
           "אינה יוצרת כפילויות:")
    CODE(doc, """
@staticmethod
def ensure_defaults(db, user):
    for name, description, per_person, essential, fixed, max_cut, importance in EXPENSE_CATEGORIES:
        category = db.query(Category).filter_by(...).first()
        if not category:
            category = Category(...); db.add(category); db.flush()
        if not db.query(CategoryStandard).filter_by(...).first():
            db.add(CategoryStandard(...))
        if not db.query(UserCategoryPreference).filter_by(...).first():
            db.add(UserCategoryPreference(...))
        if not db.query(UserCategoryGoal).filter_by(...).first():
            db.add(UserCategoryGoal(
                target_amount=per_person * (user.family_size or 1)))
    db.flush()
""", caption="HouseholdSetupService.ensure_defaults")

    H(doc, "ט׳.4  שכבת ה־DTO", 2)
    P(doc, "שכבת ה־DTO משתמשת ב־Pydantic v2 לאימות קלט "
           "ולהגדרת מבנה תשובות. לדוגמה, אימות ההרשמה:")
    CODE(doc, """
class RegistrationInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name:  str = Field(min_length=1, max_length=100)
    email:      str = Field(min_length=5, max_length=255)
    password:   str = Field(min_length=10, max_length=128)
    family_size: int = Field(ge=1, le=20)
""", caption="dto — אימות קלט הרשמה")
    P(doc, "אימות ברמת ה־DTO חוסך בדיקות חוזרות בשכבת "
           "השירותים, ומבטיח שכל קלט שמגיע ללוגיקה העסקית "
           "הוא תקין מבחינת טיפוסים וטווחים.")

    H(doc, "ט׳.5  שכבת הראוטרים (Controllers)", 2)
    P(doc, "שכבה זו חושפת את הפונקציונליות כ־API על גבי "
           "Flask Blueprints. כל תת־תחום מקבל Blueprint "
           "משלו עם url_prefix. להלן נקודות הקצה המרכזיות:")
    TABLE(doc, ["Method", "Route", "תיאור"],
          [["POST", "/auth/register", "הרשמת משק בית חדש"],
           ["POST", "/auth/login", "התחברות"],
           ["POST", "/auth/logout", "התנתקות"],
           ["GET", "/auth/me", "פרטי המשתמש המחובר"],
           ["GET", "/auth/catalog", "קטלוג קטגוריות ותקנים"],
           ["GET", "/budget/plan/<uid>/<y>/<m>", "בניית תוכנית תקציבית ושמירתה"],
           ["GET", "/budget/status", "מצב ביצוע מול התוכנית + התראות"],
           ["GET", "/budget/plans", "נתוני תוכניות גולמיים"],
           ["POST", "/expenses", "הוספת הוצאה"],
           ["POST", "/income", "הוספת הכנסה"],
           ["GET", "/api/early-warning/alerts", "התראות לחודש"],
           ["PUT", "/api/early-warning/alerts/<id>/dismiss", "דחיית התראה"],
           ["POST", "/savings/goals", "יצירת יעד חיסכון"]],
          widths=[2.2, 7.4, 5.6])

    H(doc, "ט׳.6  מידלוור האימות", 2)
    P(doc, "במקום לבדוק הרשאות בכל ראוטר בנפרד, המערכת "
           "מפעילה מידלוור גלובלי שרץ לפני כל בקשה:")
    CODE(doc, """
def register_auth_middleware(app):
    public_endpoints   = {"auth.login", "auth.register", "auth.logout",
                          "home", "static"}
    admin_endpoints    = {"auth.me", "auth.logout", "auth.households", ...}
    household_endpoints = { ... רשימת נקודות הקצה המותרות ... }

    @app.before_request
    def authenticate_request():
        if request.method == "OPTIONS" or request.endpoint in public_endpoints:
            return None
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "נדרשת התחברות"}), 401
        ...
""", caption="auth_controller.register_auth_middleware")
    P(doc, "המידלוור מבצע שלוש בדיקות מדורגות: (א) האם "
           "המשתמש מחובר; (ב) האם נקודת הקצה מותרת "
           "לתפקידו של המשתמש (הפרדה בין מנהלת למשק בית); "
           "(ג) האם המשאב המבוקש שייך למשתמש עצמו. הבדיקה "
           "השלישית מתבצעת על־ידי שליפת בעל הרשומה — "
           "למשל בעל ההוצאה לפי expense_id — והשוואה "
           "למזהה המשתמש המחובר.")
    CODE(doc, """
def _get_owned_resource(db, endpoint, arguments):
    if "expense_id" in arguments:
        row = db.query(Expense.user_id).filter(
            Expense.transaction_id == arguments["expense_id"]).first()
    elif "transaction_id" in arguments and endpoint.startswith("income."):
        row = db.query(Income.user_id).filter(...).first()
    elif "alert_id" in arguments:
        row = db.query(EarlyWarningAlert.user_id).filter(...).first()
    elif "goal_id" in arguments or (...):
        row = db.query(SavingsGoal.user_id).filter(...).first()
    else:
        return None
    return row[0] if row else False
""", caption="בדיקת בעלות על המשאב")
    P(doc, "הבדיקה מגנה על „הרשאה ברמת אובייקט” "
           "(Object-Level Authorization): משתמש מחובר "
           "שמנחש מזהה של רשומה של משק בית אחר יקבל "
           "403 — גם אם הוא עצמו מחובר כחוק. זהו אחד "
           "מהפערים הנפוצים והחמורים באפליקציות ווב, "
           "ונחסם כאן באופן שיטתי.")

    H(doc, "ט׳.7  כלי עבודה נלווים", 2)
    TABLE(doc, ["רכיב", "תפקיד"],
          [["jobs/monthly_budget_job.py", "משימה מתוזמנת להפקת תוכנית חודשית"],
           ["postman/*.json", "אוספי בדיקות API"],
           ["reset_and_seed.sql / seed_data.sql", "סקריפטי אתחול וזריעת נתונים"],
           ["main.py", "נקודת הכניסה של האפליקציה"],
           ["requirements.txt", "ניהול תלויות Python"]],
          widths=[5.6, 9.6])


def technologies(doc):
    H(doc, "י׳  טכנולוגיות וספריות בשימוש", 1, page_break=True)

    P(doc, "פרק זה מפרט את כל הטכנולוגיות והספריות "
           "שבהן נעשה שימוש בפרויקט, תוך הבחנה בין "
           "הספריות שהמערכת משתמשת בהן בפועל לבין "
           "תלויות שהוגדרו בקבצי התצורה.")

    H(doc, "י׳.1  סקירה — חלוקה לפי רכיב", 2)
    TABLE(doc, ["רכיב", "טכנולוגיה"],
          [["צד שרת", "Python, Flask, Pydantic, SQLAlchemy, Werkzeug, pyodbc"],
           ["צד לקוח", "React, TypeScript, Vite, Material UI, Emotion, React Router"],
           ["מסד נתונים", "Microsoft SQL Server (יעד) / SQLite (פיתוח)"],
           ["פרוטוקול", "HTTP + JSON, אימות מבוסס סשן"]],
          widths=[3.4, 11.8])

    H(doc, "י׳.2  טכנולוגיות צד השרת", 2)

    H(doc, "Python", 3)
    P(doc, "שפת השרת. נבחרה בזכות בהירותה, האקוסיסטם "
           "העשיר לעיבוד נתונים וניתוח מספרי, וקלות "
           "הכתיבה של לוגיקה עסקית מורכבת.")

    H(doc, "Flask", 3)
    P(doc, "מסגרת הווב הקלה שמשמשת כמסגרת הבסיס של "
           "השרת. Flask מספקת את ניהול הבקשות, הניתוב, "
           "מנגנון ה־Blueprint לפיצול האפליקציה למודולים "
           "עצמאיים, ומערכת ההקשר (context) של הבקשה. "
           "בפרויקט רשומים כשלושים Blueprints, אחד "
           "לתחום. הגדרות האבטחה של האפליקציה:")
    CODE(doc, """
app = Flask(__name__)
app.secret_key = os.environ.get("SPENDWISE_SESSION_SECRET") or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SPENDWISE_COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)
""", caption="main.py — הגדרות אבטחת הסשן")

    H(doc, "Pydantic v2", 3)
    P(doc, "ספריית אימות וסריאליזציה. משמשת הן "
           "לאימות קלט משתמש (RegistrationInput, "
           "LoginInput) והן להגדרת מבני ה־DTO. Pydantic "
           "בודקת טיפוסים, אורכים וטווחים לפני שהנתון "
           "מגיע לשכבת הלוגיקה, ומחזירה שגיאה מפורטת "
           "עבור קלט שאינו תקין.")

    H(doc, "SQLAlchemy — שכבת ה־ORM", 3)
    P(doc, "זו הספרייה המרכזית לגישה לנתונים. SQLAlchemy "
           "מספקת מיפוי אובייקטי־רלציוני (ORM): כל טבלה "
           "מיוצגת כמחלקת Python, וכל שאילתה נכתבת בשפת "
           "Python במקום SQL גולמי. היתרון המרכזי בפרויקט "
           "הוא הניידות בין מנועי מסדי נתונים.")
    P(doc, "הצד הנוסף של SQLAlchemy בשימוש כאן הוא "
           "מנגנון ה־Session, המנהל את מחזור החיים של "
           "האובייקטים, את מטמון הזהויות (identity map) "
           "ואת הטרנזקציות:")
    CODE(doc, """
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""", caption="db_connection.py — ניהול סשנים")

    H(doc, "Werkzeug", 3)
    P(doc, "ספריית העזר הבסיסית של Flask, שמשמשת "
           "בפרויקט לגיבוב סיסמאות. הסיסמה אינה נשמרת "
           "כטקסט גלוי בשום שלב:")
    CODE(doc, """
from werkzeug.security import check_password_hash, generate_password_hash

user = User(password_hash=generate_password_hash(data.password), ...)

# בעת התחברות
if not user or not check_password_hash(user.password_hash, data.password):
    return jsonify({"error": "כתובת אימייל או סיסמה שגויות"}), 401
""", caption="גיבוב סיסמאות עם Werkzeug")
    P(doc, "הפונקציה generate_password_hash מייצרת גיבוב "
           "עם מלח (salt) אקראי, וכך שתי סיסמאות זהות "
           "מקבלות גיבובים שונים. הפונקציה המקבילה "
           "check_password_hash מבצעת השוואה בזמן קבוע "
           "ומונעת התקפות תזמון.")

    H(doc, "pyodbc — מנהל התקן למסד הנתונים", 3)
    P(doc, "מנהל ההתקן שמאפשר לפייתון להתחבר ל־Microsoft "
           "SQL Server. החיבור בפרויקט מתבצע באמצעות "
           "אימות Windows:")
    CODE(doc, """
SERVER   = 'D403-013'
DATABASE = 'smart_Encomy'
DRIVER   = 'ODBC Driver 17 for SQL Server'

f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
f"&trusted_connection=yes"
""", caption="פרטי החיבור ל־SQL Server")

    H(doc, "י׳.3  טכנולוגיות צד הלקוח", 2)

    H(doc, "React 19", 3)
    P(doc, "ספריית הממשק. המערכת בנויה מרכיבים "
           "פונקציונליים (Functional Components) עם "
           "Hooks — useState לניהול מצב מקומי ו־useEffect "
           "לתופעות לוואי. לדוגמה, מסך ההתחברות מנהל "
           "מצב של מצב־טופס, שגיאות וטעינה:")
    CODE(doc, """
const [mode, setMode] = useState<'login' | 'register'>('login')
const [form, setForm] = useState<FormState>({ ... })
const [error, setError] = useState<string | null>(null)
const [loading, setLoading] = useState(false)
""", caption="client/src/components/AuthScreen.tsx — ניהול מצב")

    H(doc, "TypeScript 5.9", 3)
    P(doc, "שכבת הטיפוסים על גבי JavaScript. כל קובצי "
           "הממשק כתובים ב־TypeScript, עם הגדרת טיפוסים "
           "מפורשת למצב הרכיב ולמבני הנתונים. בטיחות "
           "הטיפוסים מזהה שגיאות כבר בזמן הכתיבה "
           "(compile time) ולא בזמן ריצה.")

    H(doc, "Vite 7", 3)
    P(doc, "כלי הבנייה (build tool) של צד הלקוח. Vite "
           "מספק שרת פיתוח עם עדכון מיידי (HMR — Hot "
           "Module Replacement) ובנייה מהירה לפרודקשן "
           "באמצעות Rollup. תצורת הפרויקט כוללת את "
           "התוספים:")
    BULLET(doc, "@vitejs/plugin-react — תמיכה ב־React כולל עיבוד JSX")
    BULLET(doc, "babel-plugin-react-compiler — מהדר הניסוי של React "
                "המבצע אופטימיזציה אוטומטית של רינדור")
    BULLET(doc, "vite-plugin-babel — חיבור Babel לתהליך הבנייה של Vite")

    H(doc, "Material UI (MUI) v7", 3)
    P(doc, "ערכת הרכיבים המשמשת את המערכת. MUI מספקת "
           "רכיבים מוכנים ומעוצבים — כפתורים, שדות "
           "קלט, כרטיסים, תיבות דו־שיח, טבלאות "
           "ופריסה (Grid). בפרויקט נעשה שימוש ברכיבי "
           "הליבה ובערכת האייקונים:")
    CODE(doc, """
import { Button, TextField, Card, Stack, Box } from '@mui/material'
import SavingsRounded from '@mui/icons-material/SavingsRounded'
import LockOutlined   from '@mui/icons-material/LockOutlined'
import ArrowBackIosNewRounded from '@mui/icons-material/ArrowBackIosNewRounded'
""", caption="שימוש ברכיבי MUI ואייקונים")

    H(doc, "Emotion", 3)
    P(doc, "ספריית ה־CSS-in-JS שמאחורי MUI. היא מאפשרת "
           "להגדיר עיצוב בתוך הקוד עצמו, עם תמיכה "
           "בערכי עיצוב דינמיים ובנושאים (themes).")
    CODE(doc, """
import styled from '@emotion/styled'
import { ThemeProvider } from '@emotion/react'
""", caption="חבילות Emotion בשימוש")

    H(doc, "React Router v7", 3)
    P(doc, "ספריית הניתוב של צד הלקוח. בפרויקט היא "
           "משמשת לחיבור מסלולי האפליקציה לרכיבים, "
           "בדפוס של ראוטר מרכזי:")
    CODE(doc, """
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const router = createBrowserRouter([{ path: '*', element: <App /> }])

// main.tsx
createRoot(document.getElementById('root')!).render(
  <RouterProvider router={routers} />
)
""", caption="ניתוב עם React Router")

    H(doc, "@fontsource/roboto", 3)
    P(doc, "חבילת גופן שמספקת את גופן Roboto כתלות "
           "מקומית — ללא תלות בקריאה לשירות גופנים "
           "חיצוני. הדבר משפר את הביצועים ואת "
           "הזמינות, ואינו מחייב יציאה לרשת.")

    H(doc, "פריסה מימין־לשמאל (RTL)", 3)
    P(doc, "המערכת מיועדת לעברית, ולכן היא מוגדרת "
           "בפריסה מימין־לשמאל. ההגדרה מתבצעת במספר "
           "רבדים: מאפיין dir=\"rtl\" על רכיבי השורש, "
           "תמיכת MUI ב־RTL, וכיווניות מתאימה בטקסטים "
           "ובאייקונים. הגישה הזו מבטיחה שהממשק יתנהג "
           "באופן טבעי לקורא העברי, ולא כ„תרגום” של "
           "ממשק לועזי.")

    H(doc, "תקשורת עם השרת", 3)
    P(doc, "המערכת משתמשת בממשק fetch המובנה של "
           "הדפדפן — ללא ספריית HTTP חיצונית. הבקשות "
           "נשלחות עם דגל credentials, וכך נשמר הסשן "
           "בצד השרת:")
    CODE(doc, """
const response = await fetch(`/auth/${mode}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify(payload),
})
const data = await response.json()
""", caption="קריאת רשת עם fetch")

    H(doc, "י׳.4  כלי פיתוח ואיכות קוד", 2)
    TABLE(doc, ["כלי", "תפקיד"],
          [["ESLint 9", "איתור בעיות ותבניות קוד ב־JavaScript/TypeScript"],
           ["typescript-eslint", "חיבור ESLint למהדר TypeScript"],
           ["TypeScript Compiler (tsc)", "בדיקת טיפוסים ובנייה"],
           ["tsconfig.app.json / tsconfig.node.json", "הגדרות טיפוסים נפרדות לאפליקציה ולסביבה"],
           ["npm / package-lock.json", "ניהול תלויות צד הלקוח בצורה נעולה"],
           ["pip / requirements.txt", "ניהול תלויות צד השרת"]],
          widths=[5.6, 9.6])

    H(doc, "י׳.5  רשימת הספריות המלאה — צד השרת", 2)
    TABLE(doc, ["ספרייה", "גרסה", "שימוש בפרויקט"],
          [["Flask", "3.1.3", "מסגרת הווב הראשית"],
           ["SQLAlchemy", "2.1.4", "ORM וניהול סשנים"],
           ["Pydantic", "2.14.1", "אימות קלט ו־DTO"],
           ["Werkzeug", "3.1.9", "גיבוב סיסמאות"],
           ["pyodbc", "5.3.0", "חיבור ל־SQL Server"],
           ["Jinja2", "3.1.6", "מנוע תבניות (תלות של Flask)"],
           ["MarkupSafe", "3.0.4", "עזר לתבניות"],
           ["itsdangerous", "2.2.0", "חתימת נתוני סשן"],
           ["click", "8.5.0", "ממשק שורת פקודה (תלות של Flask)"],
           ["blinker", "1.9.0", "מערכת אותות (Signals)"],
           ["email-validator", "2.3.0", "אימות כתובות אימייל"],
           ["typing-extensions", "4.16.0", "הרחבות טיפוסים"]],
          widths=[4.0, 2.2, 9.0])
    P(doc, "הערה: FastAPI ו־Starlette מופיעות כהגדרה "
           "בקובץ התלויות, אולם מסגרת הווב שמריצה את "
           "המערכת בפועל היא Flask. כמו כן קיימות "
           "בסביבת הפיתוח ספריות עזר ששימשו לעבודת "
           "המחקר והתיעוד (pypdf, python-bidi, python-docx) "
           "ואינן חלק ממערכת הריצה.")

    H(doc, "י׳.6  רשימת הספריות המלאה — צד הלקוח", 2)
    TABLE(doc, ["ספרייה", "גרסה", "שימוש בפועל"],
          [["react", "19.2.0", "מסגרת הממשק"],
           ["react-dom", "19.2.0", "רינדור ל־DOM"],
           ["typescript", "~5.9.3", "שכבת הטיפוסים"],
           ["vite", "7.3.1", "כלי בנייה ושרת פיתוח"],
           ["@vitejs/plugin-react", "5.1.1", "תמיכת React ב־Vite"],
           ["@mui/material", "7.3.6", "ערכת רכיבים"],
           ["@mui/icons-material", "7.3.6", "ערכת אייקונים"],
           ["@mui/styled-engine-sc", "7.3.6", "מנוע עיצוב מבוסס styled-components"],
           ["@emotion/react", "11.14.0", "עיצוב דינמי"],
           ["@emotion/styled", "11.14.1", "רכיבים מעוצבים"],
           ["@fontsource/roboto", "5.2.9", "גופן מקומי"],
           ["react-router-dom", "7.10.1", "ניתוב"],
           ["babel-plugin-react-compiler", "1.0.0", "אופטימיזציית רינדור"],
           ["vite-plugin-babel", "1.4.0", "חיבור Babel"],
           ["eslint", "9.39.1", "בדיקות קוד"],
           ["typescript-eslint", "8.48.0", "בדיקות TypeScript"]],
          widths=[5.0, 2.4, 7.8])

    H(doc, "י׳.7  הערה על תלויות שאינן בשימוש", 2)
    P(doc, "בקובץ package.json של צד הלקוח מוגדרות "
           "מספר ספריות שאינן נטענות בפועל בקוד האפליקציה: "
           "axios, react-hook-form, yup, mobx, react-mobx, "
           "redux, react-redux ו־styled-components. ספריות "
           "אלו נותרו משלב תבנית התחלתית קודמת של הפרויקט "
           "(„פרויקט ספרייה”) ואינן משמשות את מערכת "
           "„שקלול”. הדבר נבדק על־ידי סריקת כל הייבוא "
           "בקוד הלקוח.")
    P(doc, "המערכת משתמשת במקום זאת ב־fetch המובנה "
           "של הדפדפן לקריאות רשת, ובניהול מצב מקומי "
           "באמצעות hooks של React. שקיפות זו נדרשת "
           "לצורך דיוק התיעוד: אין לייחס למערכת שימוש "
           "בספרייה שאינה נטענת בפועל. מומלץ להסיר "
           "תלויות אלו בעת ניקוי הפרויקט, כדי לצמצם "
           "את משקל ההתקנה ואת שטח הפגיעות האפשרי "
           "(attack surface).")

    H(doc, "י׳.8  טבלת הטכנולוגיות המסכמת", 2)
    TABLE(doc, ["שכבה", "טכנולוגיה", "תפקיד"],
          [["ממשק משתמש", "React 19 + TypeScript", "בניית הממשק"],
           ["עיצוב", "Material UI v7 + Emotion", "רכיבים ועיצוב"],
           ["בנייה", "Vite 7", "אריזה ושרת פיתוח"],
           ["ניתוב", "React Router v7", "ניהול מסלולים"],
           ["תקשורת", "fetch + JSON", "קריאות לשרת"],
           ["שרת", "Python + Flask 3", "לוגיקת ה־API"],
           ["אימות", "Pydantic v2", "אימות קלט"],
           ["אבטחה", "Werkzeug + Session", "סיסמאות וסשנים"],
           ["ORM", "SQLAlchemy 2", "מיפוי אובייקטי"],
           ["מסד נתונים", "SQL Server / SQLite", "אחסון נתונים"],
           ["מנהל התקן", "pyodbc", "חיבור ל־SQL Server"],
           ["אבטחת קוד", "ESLint 9", "איכות הקוד"]],
          widths=[3.0, 5.4, 6.8])
