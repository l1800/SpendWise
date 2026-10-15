from pydantic import BaseModel
from datetime import date

class GoalDetailsDto(BaseModel):
    detail_id: int
    goal_id: int
    goal_type_id: int
    goal_description: str
    goal_target_date: date
    status_id: int