# dto/Finance/FinancialForecastsDto.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

# --- DTO ליצירה ---
class FinancialForecastCreateDto(BaseModel):
    user_id: int
    category_id: int
    forecast_date: date
    forecast_count: int
    range_id: int

# --- DTO לקריאה/עדכון ---
class FinancialForecastDto(FinancialForecastCreateDto):
    forecast_id: int