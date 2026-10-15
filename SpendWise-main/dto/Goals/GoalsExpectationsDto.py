from pydantic import BaseModel
from datetime import datetime, date

class GoalsExpectationsDto(BaseModel):
    expectation_id: int
    user_id: int
    goal_type_id: int
    goal_description: str
    goal_target_date: date
    status_id: int
    goal_created_date: datetime