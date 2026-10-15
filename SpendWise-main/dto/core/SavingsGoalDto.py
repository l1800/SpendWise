from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SavingsGoalCreateDTO(BaseModel):
    user_id: int
    name: str
    category_id: Optional[int] = None
    target_amount: Optional[float] = None


class SavingsGoalResponseDTO(SavingsGoalCreateDTO):
    id: int
    current_balance: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SavingsTransactionDTO(BaseModel):
    id: int
    goal_id: int
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None

    class Config:
        from_attributes = True


class OneTimeExpenseDTO(BaseModel):
    user_id: int
    goal_name: str
    amount: float
    category_id: int
    description: Optional[str] = None
