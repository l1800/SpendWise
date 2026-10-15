from pydantic import BaseModel, ConfigDict


class IncomeCategoryCreateDTO(BaseModel):
    category_name: str


class IncomeCategoryResponseDTO(BaseModel):
    category_id: int
    category_name: str

    model_config = ConfigDict(from_attributes=True)