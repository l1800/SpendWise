from pydantic import BaseModel
from datetime import date
from typing import Optional


class ReportTypeDTO(BaseModel):
    report_type_id: int
    report_type_name: str

    class Config:
        from_attributes = True


class ReportCreateDTO(BaseModel):
    user_id: int
    report_type_id: int
    report_date: date
    report_data: Optional[str] = None


class ReportResponseDTO(ReportCreateDTO):
    report_id: int

    class Config:
        from_attributes = True