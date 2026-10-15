from models.Finance.ExpenseType import ExpenseType
from repositories.base_repository import BaseRepository


class ExpenseTypesRepository(BaseRepository):

    def get_by_id(self, expense_type_id):
        return (
            self.session.query(ExpenseType)
            .filter_by(expenseTypeId=expense_type_id)
            .first()
        )

    def get_all(self):
        return self.session.query(ExpenseType).all()

    def exists_by_name(self, name):
        return (
            self.session.query(ExpenseType)
            .filter_by(expenseTypeName=name)
            .first() is not None
        )

    def update(self, expense_type_id, **kwargs):
        expense_type = self.get_by_id(expense_type_id)

        if not expense_type:
            return None

        for key, value in kwargs.items():
            setattr(expense_type, key, value)

        self.session.commit()
        return expense_type

    def delete_by_id(self, expense_type_id):
        expense_type = self.get_by_id(expense_type_id)

        if expense_type:
            self.delete(expense_type)

        return expense_type