from pydantic import BaseModel
from datetime import datetime, date


class GoalCreateDTO(BaseModel):
    user_id: int
    goal_created_date: datetime


class GoalResponseDTO(GoalCreateDTO):
    goal_id: int
    user_id: int
    goal_created_date: datetime

    class Config:
        from_attributes = True