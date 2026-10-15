from pydantic import BaseModel, ConfigDict

# DTO בסיסי (לקריאה)
class ExpenseTypeDTO(BaseModel):
    ExpenseTypeId: int
    ExpenseTypeName: str

    model_config = ConfigDict(from_attributes=True)

# DTO ליצירה/עדכון (ל־POST/PUT)
class ExpenseTypeCreateDTO(BaseModel):
    ExpenseTypeName: str