from pydantic import BaseModel



class SurveyAnswerCreateDTO(BaseModel):
    survey_id: int
    question_code: str
    question_text: str
    answer_value: int


class SurveyAnswerResponseDTO(SurveyAnswerCreateDTO):
    answer_id: int

    class Config:
        from_attributes = True