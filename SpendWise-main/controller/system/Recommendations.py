from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_connection import get_db

from dto.system.RecommendationsDto import RecommendationCreateDTO
from services.system.Recommendations import RecommendationService
from repositories.system.Recommendations import RecommendationRepository

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def get_service(db: Session = Depends(get_db)):
    repo = RecommendationRepository(db)
    return RecommendationService(repo)


@router.post("/")
def create(dto: RecommendationCreateDTO, service: RecommendationService = Depends(get_service)):
    return service.create(dto)


@router.get("/{recommendation_id}")
def get_by_id(recommendation_id: int, service: RecommendationService = Depends(get_service)):
    result = service.get_by_id(recommendation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/")
def get_all(service: RecommendationService = Depends(get_service)):
    return service.get_all()


@router.get("/user/{user_id}")
def get_by_user(user_id: int, service: RecommendationService = Depends(get_service)):
    return service.get_by_user(user_id)


@router.put("/{recommendation_id}")
def update(recommendation_id: int, dto: RecommendationCreateDTO, service: RecommendationService = Depends(get_service)):
    updated = service.update(recommendation_id, **dto.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated


@router.delete("/{recommendation_id}")
def delete(recommendation_id: int, service: RecommendationService = Depends(get_service)):
    success = service.delete(recommendation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}