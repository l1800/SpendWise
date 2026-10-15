from pydantic import BaseModel


class SpecialPeriodSummaryCreateDTO(BaseModel):
    special_period_id: int
    user_id: int
    category_id: int
    spent_amount: int
    approved_amount: int


class SpecialPeriodSummaryResponseDTO(
    SpecialPeriodSummaryCreateDTO
):
    summary_id: int

    class Config:
        from_attributes = True