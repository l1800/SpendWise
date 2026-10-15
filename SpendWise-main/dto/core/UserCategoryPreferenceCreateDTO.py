from pydantic import BaseModel


class UserCategoryPreferenceCreateDTO(BaseModel):
    user_id: int
    category_id: int
    importance_score: float