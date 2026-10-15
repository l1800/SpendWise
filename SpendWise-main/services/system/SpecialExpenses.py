from typing import List, Optional
from dto.system.SpecialExpenseDto import SpecialExpenseCreateDTO, SpecialExpenseResponseDTO
from repositories.system.SpecialExpenses import SpecialExpensesRepository

class SpecialExpenseService:

    def __init__(self, repository: SpecialExpensesRepository):
        self.repository = repository

    def create(self, dto: SpecialExpenseCreateDTO) -> SpecialExpenseResponseDTO:
        obj = self.repository.create(dto.dict())
        return SpecialExpenseResponseDTO.model_validate(obj)

    def get_by_id(self, special_expense_id: int) -> Optional[SpecialExpenseResponseDTO]:
        obj = self.repository.get_by_id(special_expense_id)
        return SpecialExpenseResponseDTO.model_validate(obj) if obj else None

    def get_all(self) -> List[SpecialExpenseResponseDTO]:
        return [SpecialExpenseResponseDTO.model_validate(x) for x in self.repository.get_all()]

    def get_by_user(self, user_id: int) -> List[SpecialExpenseResponseDTO]:
        return [SpecialExpenseResponseDTO.model_validate(x) for x in self.repository.get_by_user(user_id)]

    def update(self, special_expense_id: int, **kwargs):
        obj = self.repository.update(special_expense_id, **kwargs)
        return SpecialExpenseResponseDTO.model_validate(obj) if obj else None

    def delete(self, special_expense_id: int) -> bool:
        return self.repository.delete_by_id(special_expense_id) is not None