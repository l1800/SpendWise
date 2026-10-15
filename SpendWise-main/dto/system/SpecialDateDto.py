from pydantic import BaseModel
from datetime import date

class SpecialDateCreateDTO(BaseModel):
    holiday_name: str
    start_date: date
    end_date: date

class SpecialDateResponseDTO(SpecialDateCreateDTO):
    type_id: int

    class Config:
        from_attributes = True