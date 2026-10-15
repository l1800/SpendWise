
        """
        from pydantic import BaseModel


class CategoryTypeDTO(BaseModel):
    category_type_id: int
    category_type_name: str

    class Config:
        from_attributes = True
"""