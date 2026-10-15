from typing import List, Optional
from datetime import datetime

from dto.core.UserCategoryGoalDto import (
    UserCategoryGoalCreateDTO,
    UserCategoryGoalResponseDTO
)

from repositories.core.UserCategoryGoalRepository import UserCategoryGoalRepository


class UserCategoryGoalService:

    def __init__(self, repository: UserCategoryGoalRepository):
        self.repository = repository

    def get_all(self) -> List[UserCategoryGoalResponseDTO]:
        return [
            UserCategoryGoalResponseDTO.model_validate(x)
            for x in self.repository.get_all()
        ]

    def get_by_id(self, id: int) -> Optional[UserCategoryGoalResponseDTO]:
        obj = self.repository.get_by_id(id)
        return UserCategoryGoalResponseDTO.model_validate(obj) if obj else None

    def get_by_user(self, user_id: int) -> List[UserCategoryGoalResponseDTO]:
        return [
            UserCategoryGoalResponseDTO.model_validate(x)
            for x in self.repository.get_by_user(user_id)
        ]

    def get_by_user_and_category(self, user_id: int, category_id: int) -> Optional[UserCategoryGoalResponseDTO]:
        obj = self.repository.get_by_user_and_category(user_id, category_id)
        return UserCategoryGoalResponseDTO.model_validate(obj) if obj else None

    def create(self, dto: UserCategoryGoalCreateDTO) -> UserCategoryGoalResponseDTO:
        obj = self.repository.create(
            obj_data={
                "user_id": dto.user_id,
                "category_id": dto.category_id,
                "target_amount": dto.target_amount,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )

        return UserCategoryGoalResponseDTO.model_validate(obj)

    def update(self, id: int, target_amount) -> Optional[UserCategoryGoalResponseDTO]:
        obj = self.repository.update(
            id,
            target_amount=target_amount,
            updated_at=datetime.utcnow()
        )

        return UserCategoryGoalResponseDTO.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete_by_id(id) is not None