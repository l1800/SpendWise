from models.core.UserCategoryGoal import UserCategoryGoal
from models.core.CategoryStandard import CategoryStandard
from models.core.Users import User
from repositories.base_repository import BaseRepository


class UserCategoryGoalRepository(BaseRepository):

    # ================= BASIC CRUD =================

    def get_by_id(self, id):
        return (
            self.session.query(UserCategoryGoal)
            .filter_by(id=id)
            .first()
        )

    def get_all(self):
        return self.session.query(UserCategoryGoal).all()

    def get_by_user(self, user_id):
        return (
            self.session.query(UserCategoryGoal)
            .filter_by(user_id=user_id)
            .all()
        )

    def get_by_user_and_category(self, user_id, category_id):
        return (
            self.session.query(UserCategoryGoal)
            .filter_by(user_id=user_id, category_id=category_id)
            .first()
        )

    def create(self, obj_data):
        obj = UserCategoryGoal(**obj_data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, id, **kwargs):
        obj = self.get_by_id(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    # ================= CORE LOGIC =================

    def recalculate_for_user(self, user_id):
        """
        מחשב מחדש את כל היעדים החודשיים לפי קטגוריות עבור משתמש.
        לוגיקה: target_amount = amount_per_person × family_size
        לכל קטגוריה ב-Category_Standards.

        מבצע UPSERT — אם כבר קיים יעד לקטגוריה, מעדכן; אחרת יוצר חדש.
        """
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return []

        family_size = user.family_size or 1

        standards = self.session.query(CategoryStandard).all()

        results = []
        for std in standards:
            target = std.amount_per_person * family_size

            existing = self.get_by_user_and_category(user_id, std.category_id)

            if existing:
                existing.target_amount = target
                existing.updated_at = None  # יקבע אוטומטית כ-utcnow
            else:
                existing = UserCategoryGoal(
                    user_id=user_id,
                    category_id=std.category_id,
                    target_amount=target
                )
                self.session.add(existing)

            results.append(existing)

        self.session.commit()

        for r in results:
            self.session.refresh(r)

        return results

    def get_targets_map(self, user_id):
        """
        מחזיר dict: {category_id: target_amount} עבור משתמש.
        """
        rows = self.get_by_user(user_id)
        return {r.category_id: r.target_amount for r in rows}
