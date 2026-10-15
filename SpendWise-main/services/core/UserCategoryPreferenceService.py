class UserCategoryPreferenceService:

    def __init__(self, pref_repo, category_repo):
        self.pref_repo = pref_repo
        self.category_repo = category_repo

    # =========================
    # VALIDATION
    # =========================
    def validate_category_exists(self, category_id):

        category = self.category_repo.get_by_id(category_id)

        if not category:
            raise ValueError("Category does not exist")

        return category

    # =========================
    # SAVE
    # =========================
    def save_preferences(self, dto_list):

        for dto in dto_list:
            self.validate_category_exists(dto.category_id)
            self.pref_repo.upsert(dto)

    # =========================
    # MAP
    # =========================
    def get_preferences_map(self, user_id):

        rows = self.pref_repo.get_by_user(user_id)

        return {
            r.category_id: r.importance_score
            for r in rows
        }

    # =========================
    # NORMALIZE
    # =========================
    @staticmethod
    def normalize_score(score):

        if score <= 1:
            score = score * 100

        if score < 0:
            return 0

        if score > 100:
            return 100

        return float(score)

    # =========================
    # CORE ENGINE
    # =========================
    def get_category_importance(self, user_id, category_id):

        # 1. ניסיון אישי
        user_pref = self.pref_repo.get_by_user_and_category(user_id, category_id)

        if user_pref:
            return self.normalize_score(user_pref.importance_score)

        # 2. fallback לסטנדרט (דרך קטגוריה בלבד)
        category = self.category_repo.get_by_id(category_id)

        if category:
            return 60.0

        # 3. ברירת מחדל
        return 50.0