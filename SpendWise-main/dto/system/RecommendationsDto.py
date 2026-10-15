from pydantic import BaseModel
from datetime import date


class TextDTO(BaseModel):
    text_id: int
    the_text: str

    class Config:
        from_attributes = True


class RecommendationCreateDTO(BaseModel):
    user_id: int
    text_id: int
    recommendation_date: date


class RecommendationResponseDTO(RecommendationCreateDTO):
    recommendation_id: int

    class Config:
        from_attributes = True