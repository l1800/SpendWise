from pydantic import BaseModel
from datetime import date
from typing import Optional

class SatisfactionSurveyCreateDTO(BaseModel):
    user_id: int
    survey_date: date
    feedback: Optional[str] = None

class SatisfactionSurveyResponseDTO(SatisfactionSurveyCreateDTO):
    survey_id: int

    class Config:
        from_attributes = True