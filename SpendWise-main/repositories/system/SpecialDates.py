from models.system.SpecialDate import SpecialDate
from repositories.base_repository import BaseRepository


class SpecialDateRepository(BaseRepository):

    def get_by_id(self, type_id: int) -> SpecialDate | None:
        return (
            self.session.query(SpecialDate)
            .filter_by(type_id=type_id)
            .first()
        )

    def get_all(self) -> list[SpecialDate]:
        return self.session.query(SpecialDate).all()

    def exists_by_name(self, holiday_name: str) -> bool:
        return (
            self.session.query(SpecialDate)
            .filter_by(holiday_name=holiday_name)
            .first() is not None
        )

    def update(self, type_id: int, **kwargs) -> SpecialDate | None:
        special_date = self.get_by_id(type_id)
        if not special_date:
            return None

        for key, value in kwargs.items():
            setattr(special_date, key, value)

        self.session.commit()
        return special_date

    def delete_by_id(self, type_id: int) -> SpecialDate | None:
        special_date = self.get_by_id(type_id)
        if special_date:
            self.delete(special_date)
        return special_date