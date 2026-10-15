from pydantic import BaseModel


class SpecialDateTypeDTO(BaseModel):
    type_id: int
    type_name: str

    class Config:
        from_attributes = True