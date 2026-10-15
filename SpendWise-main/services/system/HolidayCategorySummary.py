from typing import List, Optional
from datetime import datetime

from dto.system.HolidayCategorySummaryDto import (
    HolidayCategorySummaryCreateDTO,
    HolidayCategorySummaryResponseDTO
)

from repositories.system.HolidayCategorySummary import HolidayCategorySummaryRepository


class HolidayCategorySummaryService:

    def __init__(self, repository: HolidayCategorySummaryRepository):
        self.repository = repository

    def get_all(self) -> List[HolidayCategorySummaryResponseDTO]:
        return [
            HolidayCategorySummaryResponseDTO.model_validate(x)
            for x in self.repository.get_all()
        ]

    def get_by_id(self, summary_id: int) -> Optional[HolidayCategorySummaryResponseDTO]:
        obj = self.repository.get_by_id(summary_id)
        return HolidayCategorySummaryResponseDTO.model_validate(obj) if obj else None

    def get_by_user(self, user_id: int) -> List[HolidayCategorySummaryResponseDTO]:
        return [
            HolidayCategorySummaryResponseDTO.model_validate(x)
            for x in self.repository.get_by_user(user_id)
        ]

    def get_by_user_and_category(self, user_id: int, category_id: int) -> Optional[HolidayCategorySummaryResponseDTO]:
        obj = self.repository.get_by_user_and_category(user_id, category_id)
        return HolidayCategorySummaryResponseDTO.model_validate(obj) if obj else None

    def create(self, dto: HolidayCategorySummaryCreateDTO) -> HolidayCategorySummaryResponseDTO:
        obj = self.repository.create(
            obj_data={
                "user_id": dto.user_id,
                "category_id": dto.category_id,
                "change_ratio": dto.change_ratio,
                "last_calculated": datetime.utcnow()
            }
        )
        return HolidayCategorySummaryResponseDTO.model_validate(obj)

    def update(self, summary_id: int, change_ratio) -> Optional[HolidayCategorySummaryResponseDTO]:
        obj = self.repository.update(
            summary_id,
            change_ratio=change_ratio,
            last_calculated=datetime.utcnow()
        )
        return HolidayCategorySummaryResponseDTO.model_validate(obj) if obj else None

    def delete(self, summary_id: int) -> bool:
        return self.repository.delete_by_id(summary_id) is not None