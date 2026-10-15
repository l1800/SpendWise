from pydantic import BaseModel
from datetime import date



class ExpenseTypeDTO(BaseModel):
    ExpenseTypeId: int
    ExpenseTypeName: str

    class Config:
        from_attributes = True


class ExpenseCreateDTO(BaseModel):
    user_id: int
    amount: float
    date: date
    expense_type_id: int
    category_id: int
class ExpenseResponseDTO(BaseModel):
    transaction_id: int
    user_id: int
    amount: float
    date: date
    expense_type_id: int
    category_id: int

    class Config:
        from_attributes = True