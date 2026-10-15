from pydantic import BaseModel
from datetime import date


class ForecastRangeDTO(BaseModel):
    range_name: str

    class Config:
        from_attributes = True


class FinancialForecastCreateDTO(BaseModel):
    user_id: int
    category_id: int
    forecast_date: date
    count: int
    range_id: int


class FinancialForecastResponseDTO(FinancialForecastCreateDTO):
    forecast_id: int

    class Config:
        from_attributes = True