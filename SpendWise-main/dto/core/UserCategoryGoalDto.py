from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic import Field


class UserCategoryGoalCreateDTO(BaseModel):
    user_id: int
    category_id: int
    target_amount: float = Field(ge=0)


class UserCategoryGoalResponseDTO(BaseModel):
    id: int
    user_id: int
    category_id: int
    target_amount: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
