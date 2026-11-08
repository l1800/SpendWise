<div dir="rtl">

# שקלול — SpendWise

מערכת חכמה לניהול כלכלת הבית: ניתוח המצב הפיננסי, דירוג קטגוריות לקיצוץ, בניית תקציב חודשי והפקת המלצות.

- **Backend:** Python (Flask) + SQLAlchemy
- **Frontend:** React 19 + TypeScript + Vite + MUI
- **מסד נתונים:** SQL Server (`smart_Encomy`) או SQLite להתפתחות מקומית

---

## מה המערכת עושה

| שלב | תיאור |
|-----|-------|
| 1. מצב פיננסי | חישוב כסף פנוי חודשי, הוצאות לפי קטגוריה, תקציב סטנדרטי לפי גודל המשפחה |
| 2. ניתוח | ציון לחץ פיננסי משולב (חריגות, מגמות התנהגותיות, לחץ תקציבי) |
| 3. התאמה אישית | חשיבות אישית לכל קטגוריה, הפרדה בין חובה לגמיש |
| 4. קבלת החלטות | דירוג קטגוריות לקיצוץ, חישוב סכום הקיצוץ וחלוקה בפועל |
| 5. בניית תקציב | תוכנית תקציבית לחודש הבא, כולל התאמת תקופות חג |
| 6. התראות | Early Warning System — חריגות מתקציב, קפיצות חריגות בהוצאה בודדת |

### מסכים בממשק
- **מסך התקציב החכם** — תוכנית, מצב ביצוע והתראות
- **מרכז הניהול והמעקב** — סקירה, מגמות וציון בריאות פיננסית (למנהל)
- **ניהול משק בית** — הרשמה, התחברות וניהול חברי המשפחה

---

## מבנה הפרויקט

```
SpendWise/
├── main.py                 # נקודת הכניסה — Flask app
├── db_connection.py        # חיבור SQLAlchemy למסד הנתונים
├── models/                 # SQLAlchemy ORM
├── repositories/           # שכבת גישה לנתונים
├── services/               # לוגיקה עסקית (budget, FinancialHealth, CutRanking...)
├── controller/             # Flask Blueprints (API)
├── dto/                    # אובייקטי העברה
├── jobs/                   # משימות מתוזמנות
├── client/                 # Frontend React + TypeScript
├── seed_demo_spendwise.sql # נתוני דמו
└── requirements.txt
```

---

## התקנה והרצה

### דרישות מוקדמות
- Python 3.11+
- Node.js 20+
- (אופציונלי) Microsoft ODBC Driver 17 for SQL Server

### 1. Backend

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

**בחירת מסד נתונים:**

ברירת המחדל היא SQL Server בשרת `D403-013`. להרצה מקומית עם SQLite:

```bash
# Windows (cmd)
set SPENDWISE_DATABASE_URL=sqlite:///spendwise-dev.db
# PowerShell
$env:SPENDWISE_DATABASE_URL="sqlite:///spendwise-dev.db"
# Linux / macOS
export SPENDWISE_DATABASE_URL="sqlite:///spendwise-dev.db"
```

הרצה:

```bash
python main.py
```

השרת יעלה על `http://localhost:5000`.

### 2. Frontend

```bash
cd client
npm install
npm run dev
```

הממשק יעלה על `http://localhost:5173`. ה-Vite מוגדר כ-proxy לכל בקשות ה-API אל `localhost:5000` (ראו `client/vite.config.ts`).

---

## משתני סביבה

| משתנה | ברירת מחדל | תיאור |
|--------|-------------|--------|
| `SPENDWISE_DATABASE_URL` | SQL Server (`D403-013/smart_Encomy`) | מחרוזת חיבור SQLAlchemy |
| `SPENDWISE_SESSION_SECRET` | אקראי בכל הפעלה | מפתח לחתימת session — **חובה להגדיר בייצור** |
| `SPENDWISE_COOKIE_SECURE` | `0` | `1` לחיבור HTTPS בלבד |
| `SPENDWISE_SQL_ECHO` | `0` | `1` להדפסת שאילתות SQL |

---

## דגשים לייצור

- הגדירו `SPENDWISE_SESSION_SECRET` קבוע — אחרת כל הפעלה מנתקת את כל המשתמשים.
- הגדירו `SPENDWISE_COOKIE_SECURE=1` מאחורי HTTPS.
- כבו `debug=True` ב-`main.py`.

---

## הערות

- מסמך תיעוד מפורט של הארכיטקטורה נמצא ב-`CLAUDE.md`.
- פרטי מערכת ההתחברות נמצאים ב-`AUTH_SETUP.md`.

</div>
