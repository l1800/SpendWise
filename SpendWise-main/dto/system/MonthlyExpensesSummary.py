from pydantic import BaseModel


class MonthlyExpensesSummaryCreateDTO(BaseModel):
    user_id: int
    category_id: int
    month_year: str
    total_amount: int


class MonthlyExpensesSummaryResponseDTO(MonthlyExpensesSummaryCreateDTO):
    summary_id: int

    class Config:
        from_attributes = True