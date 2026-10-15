from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EarlyWarningAlertCreateDto(BaseModel):
    user_id: int
    category_id: Optional[int] = None
    year: int
    month: int
    alert_type: str
    severity: str
    title: str
    message: Optional[str] = None
    budget_amount: Optional[float] = None
    spent_so_far: Optional[float] = None

class EarlyWarningAlertResponseDto(BaseModel):
    alert_id: int
    user_id: int
    category_id: Optional[int] = None
    year: int
    month: int
    alert_type: str
    severity: str
    title: str
    message: Optional[str] = None
    budget_amount: Optional[float] = None
    spent_so_far: Optional[float] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
