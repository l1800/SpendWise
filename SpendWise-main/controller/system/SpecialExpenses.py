from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_connection import get_db
from dto.system.SpecialExpenseDto import SpecialExpenseCreateDTO
from repositories.system.SpecialExpenses import SpecialExpensesRepository
from services.system.SpecialExpenses import SpecialExpenseService

router = APIRouter(prefix="/special-expenses", tags=["Special Expenses"])

def get_service(db: Session = Depends(get_db)):
    repo = SpecialExpensesRepository(db)
    return SpecialExpenseService(repo)

@router.post("/")
def create(dto: SpecialExpenseCreateDTO, service: SpecialExpenseService = Depends(get_service)):
    return service.create(dto)

@router.get("/")
def get_all(service: SpecialExpenseService = Depends(get_service)):
    return service.get_all()

@router.get("/{special_expense_id}")
def get_by_id(special_expense_id: int, service: SpecialExpenseService = Depends(get_service)):
    result = service.get_by_id(special_expense_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result

@router.get("/user/{user_id}")
def get_by_user(user_id: int, service: SpecialExpenseService = Depends(get_service)):
    return service.get_by_user(user_id)

@router.put("/{special_expense_id}")
def update(special_expense_id: int, service: SpecialExpenseService = Depends(get_service), **kwargs):
    result = service.update(special_expense_id, **kwargs)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result

@router.delete("/{special_expense_id}")
def delete(special_expense_id: int, service: SpecialExpenseService = Depends(get_service)):
    success = service.delete(special_expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}