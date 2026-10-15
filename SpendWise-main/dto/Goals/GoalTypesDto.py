from pydantic import BaseModel

class GoalTypesDto(BaseModel):
    goal_type_id: int
    goal_type_name: str