from typing import List, Optional
from dto.system.SpecialDateTypeDto import SpecialDateTypeDTO
from repositories.system.SpecialDateTypes import (
    SpecialDateTypesRepository
)


class SpecialDateTypesService:

    def __init__(self, repository: SpecialDateTypesRepository):
        self.repository = repository

    def get_all(self) -> List[SpecialDateTypeDTO]:
        return [
            SpecialDateTypeDTO.model_validate(x)
            for x in self.repository.get_all()
        ]

    def get_by_id(self, type_id: int) -> Optional[SpecialDateTypeDTO]:
        obj = self.repository.get_by_id(type_id)
        return SpecialDateTypeDTO.model_validate(obj) if obj else None

    def create(self, type_name: str) -> SpecialDateTypeDTO:
        obj = self.repository.create(type_name)
        return SpecialDateTypeDTO.model_validate(obj)

    def update(self, type_id: int, type_name: str):
        obj = self.repository.update(
            type_id,
            type_name=type_name
        )

        return (
            SpecialDateTypeDTO.model_validate(obj)
            if obj else None
        )

    def delete(self, type_id: int) -> bool:
        return self.repository.delete_by_id(type_id)