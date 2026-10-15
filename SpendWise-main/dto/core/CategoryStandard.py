from pydantic import BaseModel


class CategoryStandardBaseDTO(BaseModel):
    category_id: int
    amount_per_person: float | None = None
    is_fixed_cost: bool
    is_essential: bool
    rule_description: str | None = None
    max_cut_percent = 100


class CategoryStandardCreateDTO(CategoryStandardBaseDTO):
    pass


class CategoryStandardResponseDTO(CategoryStandardBaseDTO):
    benchmark_id: int

    class Config:
        from_attributes = True