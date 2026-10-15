# dto/reporting/ReportTypesDto.py

from pydantic import BaseModel, ConfigDict


class ReportTypeCreateDTO(BaseModel):
    report_type_name: str


class ReportTypeResponseDTO(ReportTypeCreateDTO):
    report_type_id: int

    model_config = ConfigDict(from_attributes=True)