from dto.Finance.ExpenseTypeDto import ExpenseTypeDTO, ExpenseTypeCreateDTO
from repositories.Finance.ExpenseTypes import ExpenseTypesRepository
from models.Finance.ExpenseType import ExpenseType


class ExpenseTypeService:
    def __init__(self, repository: ExpenseTypesRepository):
        self.repo = repository

    # --- CREATE ---
    def add_expense_type(self, dto: ExpenseTypeCreateDTO) -> ExpenseType:
        expense_type = ExpenseType(
            expenseTypeName=dto.ExpenseTypeName
        )
        self.repo.add(expense_type)
        return expense_type

    # --- READ ALL ---
    def get_all_expense_types(self):
        return self.repo.get_all()

    # --- READ BY ID ---
    def get_expense_type_by_id(self, expense_type_id: int):
        return self.repo.get_by_id(expense_type_id)

    # --- UPDATE ---
    def update_expense_type(self, expense_type_id: int, dto: ExpenseTypeCreateDTO):
        return self.repo.update(
            expense_type_id,
            expenseTypeName=dto.ExpenseTypeName
        )

    # --- DELETE ---
    def delete_expense_type(self, expense_type_id: int):
        return self.repo.delete_by_id(expense_type_id)