from models.core.UserSavingGoal import UserSavingGoal
from repositories.base_repository import BaseRepository


class UserSavingGoalRepository(BaseRepository):

    def get_for_month(self, user_id, year, month):
        """מחזיר את כל הקצאות החיסכון של המשתמש לחודש מסוים."""
        return (
            self.session.query(UserSavingGoal)
            .filter_by(user_id=user_id, year=year, month=month)
            .all()
        )

    def get_all_for_user(self, user_id):
        """הכל — כל החודשים."""
        return (
            self.session.query(UserSavingGoal)
            .filter_by(user_id=user_id)
            .order_by(UserSavingGoal.year.desc(), UserSavingGoal.month.desc())
            .all()
        )

    def create_initial_for_month(self, user_id, year, month, goals):
        """
        יוצר רשומות ראשוניות (amount=0) לכל יעדי החיסכון של המשתמש.
        קוראים לזה בתחילת חודש — לפני שהמשתמש ממלא סכומים.

        goals: list of SavingsGoal
        """
        for goal in goals:
            record = UserSavingGoal(
                user_id=user_id,
                goal_id=goal.id,
                year=year,
                month=month,
                allocated_amount=0,
                applied=0,
            )
            self.session.add(record)
        self.session.commit()

    def update_allocation(self, user_id, year, month, allocations):
        """
        המשתמש מעדכן סכומים.
        allocations: [{"goal_id": 1, "amount": 1000}, ...]
        """
        records = self.get_for_month(user_id, year, month)
        alloc_map = {a["goal_id"]: a["amount"] for a in allocations}

        for record in records:
            if record.goal_id in alloc_map:
                record.allocated_amount = alloc_map[record.goal_id]

        self.session.commit()
        return records

    def get_pending_allocations(self, user_id, year, month):
        """הקצאות שלא בוצעו עדיין (applied=0)."""
        return (
            self.session.query(UserSavingGoal)
            .filter_by(user_id=user_id, year=year, month=month, applied=0)
            .all()
        )

    def mark_applied(self, record):
        """מסמן הקצאה כבוצעה."""
        record.applied = 1
        self.session.commit()
