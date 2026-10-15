from models.system.SpecialExpense import SpecialExpense
from repositories.base_repository import BaseRepository


class SpecialExpensesRepository(BaseRepository):

    def get_by_id(self, special_expense_id):
        return (
            self.session.query(SpecialExpense)
            .filter_by(special_expense_id=special_expense_id)
            .first()
        )

    def get_all(self):
        return self.session.query(SpecialExpense).all()

    def get_by_user(self, user_id):
        return (
            self.session.query(SpecialExpense)
            .filter_by(user_id=user_id)
            .all()
        )

    def update(self, special_expense_id, **kwargs):
        expense = self.get_by_id(special_expense_id)

        if not expense:
            return None

        for key, value in kwargs.items():
            setattr(expense, key, value)

        self.session.commit()
        return expense

    def delete_by_id(self, special_expense_id):
        expense = self.get_by_id(special_expense_id)

        if expense:
            self.delete(expense)

        return expense