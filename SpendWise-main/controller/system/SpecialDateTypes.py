from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_connection import get_db
from services.system.SpecialDateTypes import (
    SpecialDateTypesService
)
from repositories.system.SpecialDateTypes import (
    SpecialDateTypesRepository
)

router = APIRouter(
    prefix="/special-date-types",
    tags=["Special Date Types"]
)


def get_service(
    db: Session = Depends(get_db)
):
    repo = SpecialDateTypesRepository(db)
    return SpecialDateTypesService(repo)


@router.get("/")
def get_all(
    service: SpecialDateTypesService = Depends(get_service)
):
    return service.get_all()


@router.get("/{type_id}")
def get_by_id(
    type_id: int,
    service: SpecialDateTypesService = Depends(get_service)
):
    result = service.get_by_id(type_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    return result


@router.post("/")
def create(
    type_name: str,
    service: SpecialDateTypesService = Depends(get_service)
):
    return service.create(type_name)


@router.put("/{type_id}")
def update(
    type_id: int,
    type_name: str,
    service: SpecialDateTypesService = Depends(get_service)
):
    result = service.update(
        type_id,
        type_name
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    return result


@router.delete("/{type_id}")
def delete(
    type_id: int,
    service: SpecialDateTypesService = Depends(get_service)
):
    success = service.delete(type_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    return {"success": True}