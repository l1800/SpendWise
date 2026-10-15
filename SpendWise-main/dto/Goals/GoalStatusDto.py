from pydantic import BaseModel


class GoalStatusDTO(BaseModel):
    status_id: int
    status_name: str

    class Config:
        from_attributes = True