from pydantic import BaseModel
from datetime import datetime


class SpecialExpenseCreateDTO(BaseModel):
    user_id: int
    category_id: int
    special_date_id: int
    total_amount: int


class SpecialExpenseResponseDTO(SpecialExpenseCreateDTO):
    special_expense_id: int
    created_at: datetime

    class Config:
        from_attributes = True