from models.system.SpecialDateType import SpecialDateType
from repositories.base_repository import BaseRepository


class SpecialDateTypesRepository(BaseRepository):

    def create(self, type_name: str):
        obj = SpecialDateType(type_name=type_name)

        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)

        return obj

    def get_by_id(self, type_id):
        return (
            self.session.query(SpecialDateType)
            .filter_by(type_id=type_id)
            .first()
        )

    def get_all(self):
        return self.session.query(SpecialDateType).all()

    def update(self, type_id, **kwargs):
        special_type = self.get_by_id(type_id)

        if not special_type:
            return None

        for key, value in kwargs.items():
            setattr(special_type, key, value)

        self.session.commit()
        self.session.refresh(special_type)

        return special_type

    def delete_by_id(self, type_id):
        special_type = self.get_by_id(type_id)

        if not special_type:
            return False

        self.session.delete(special_type)
        self.session.commit()

        return True