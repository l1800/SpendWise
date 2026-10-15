from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class HolidayCategorySummaryCreateDTO(BaseModel):
    user_id: int
    category_id: int
    change_ratio: Decimal


class HolidayCategorySummaryResponseDTO(HolidayCategorySummaryCreateDTO):
    summary_id: int
    last_calculated: datetime

    class Config:
        from_attributes = True