from pydantic import BaseModel
from datetime import date


class IncomeCreateDTO(BaseModel):
    user_id: int
    frequency_id: int
    category_id: int
    amount: float
    date: date


class IncomeResponseDTO(BaseModel):
    transaction_id: int
    user_id: int
    frequency_id: int
    category_id: int
    amount: float
    date: date

    class Config:
        from_attributes = True