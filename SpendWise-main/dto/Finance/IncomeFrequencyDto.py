from pydantic import BaseModel


class IncomeFrequencyDTO(BaseModel):
    frequency_id: int
    frequency_name: str

    class Config:
        from_attributes = True