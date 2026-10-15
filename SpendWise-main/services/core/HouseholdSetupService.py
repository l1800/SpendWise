from models.core.Categories import Category
from models.core.CategoryStandard import CategoryStandard
from models.core.UserCategoryGoal import UserCategoryGoal
from models.core.UserCategoryPreference import UserCategoryPreference
from models.Finance.ExpenseType import ExpenseType
from models.Finance.IncomeCategory import IncomeCategory
from models.Finance.IncomeFrequency import IncomeFrequency
from models.lookups.CategogyType import CategoryType


EXPENSE_CATEGORIES = [
    ("שכירות / משכנתא", "תשלום דיור חודשי", 1050, True, True, 0, 100),
    ("חשבונות חשמל ומים", "חשבונות בית שוטפים", 180, True, False, 20, 82),
    ("ארנונה", "תשלום עירוני תקופתי", 110, True, True, 0, 92),
    ("מזון וסופרמרקט", "קניות מזון ומוצרי בית", 520, True, False, 15, 78),
    ("חינוך וילדים", "מסגרות, צהרון וחוגים", 430, True, False, 10, 88),
    ("רכב ותחבורה", "דלק ותחבורה שוטפת", 220, False, False, 30, 58),
    ("בריאות", "רופאים, תרופות וטיפולים", 170, True, False, 5, 96),
    ("ביגוד והנעלה", "ביגוד והנעלה למשפחה", 120, False, False, 45, 42),
    ("בילויים ומסעדות", "פנאי ואוכל מחוץ לבית", 140, False, False, 60, 32),
    ("צדקה ומעשרות", "תרומות ומעשרות", 150, False, False, 25, 68),
    ("חסכונות והשקעות", "חיסכון חודשי והשקעות", 200, False, False, 50, 72),
    ("תקשורת", "אינטרנט וטלפונים", 85, True, False, 20, 74),
    ("ריהוט וציוד לבית", "ציוד לבית והחלפות", 90, False, False, 50, 38),
    ("חופשות ונופש", "חופשות ונופש משפחתי", 120, False, False, 65, 30),
    ("הלוואות", "החזרי הלוואות חודשיים", 330, True, True, 0, 100),
    ("מתנות ושמחות", "אירועים ומתנות", 90, False, False, 45, 48),
    ("הוצאות שונות", "הוצאות מזדמנות", 110, False, False, 35, 50),
]

INCOME_CATEGORIES = ("משכורת", "עסק", "קצבה", "הכנסה אחרת")
EXPENSE_TYPES = ("רגילה", "קבועה", "חד פעמית", "חירום")
INCOME_FREQUENCIES = ("חודשי", "חד פעמי", "רבעוני", "שנתי")


class HouseholdSetupService:
    """Create shared catalogs and missing per-household targets/preferences."""

    @staticmethod
    def ensure_defaults(db, user):
        types = {}
        for name in ("expense", "income"):
            item = db.query(CategoryType).filter_by(category_type_name=name).first()
            if not item:
                item = CategoryType(category_type_name=name)
                db.add(item)
                db.flush()
            types[name] = item

        for name, description, per_person, essential, fixed, max_cut, importance in EXPENSE_CATEGORIES:
            category = db.query(Category).filter_by(
                category_name=name,
                category_type_id=types["expense"].category_type_id,
            ).first()
            if not category:
                category = Category(
                    category_name=name,
                    category_type_id=types["expense"].category_type_id,
                    category_description=description,
                )
                db.add(category)
                db.flush()

            standard = db.query(CategoryStandard).filter_by(category_id=category.category_id).first()
            if not standard:
                standard = CategoryStandard(
                    category_id=category.category_id,
                    amount_per_person=per_person,
                    is_essential=essential,
                    is_fixed_cost=fixed,
                    rule_description=description,
                    max_cut_percent=max_cut,
                )
                db.add(standard)

            if not db.query(UserCategoryPreference).filter_by(
                user_id=user.user_id, category_id=category.category_id
            ).first():
                db.add(UserCategoryPreference(
                    user_id=user.user_id,
                    category_id=category.category_id,
                    importance_score=importance,
                ))

            if not db.query(UserCategoryGoal).filter_by(
                user_id=user.user_id, category_id=category.category_id
            ).first():
                db.add(UserCategoryGoal(
                    user_id=user.user_id,
                    category_id=category.category_id,
                    target_amount=per_person * (user.family_size or 1),
                ))

        for name in INCOME_CATEGORIES:
            if not db.query(IncomeCategory).filter_by(category_name=name).first():
                db.add(IncomeCategory(category_name=name))
        for name in EXPENSE_TYPES:
            if not db.query(ExpenseType).filter_by(expenseTypeName=name).first():
                db.add(ExpenseType(expenseTypeName=name))
        for name in INCOME_FREQUENCIES:
            if not db.query(IncomeFrequency).filter_by(frequency_name=name).first():
                db.add(IncomeFrequency(frequency_name=name))

        db.flush()
