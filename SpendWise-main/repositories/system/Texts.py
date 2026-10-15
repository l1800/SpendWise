from models.system.Texts import Text
from repositories.base_repository import BaseRepository


class TextsRepository(BaseRepository):

    def create(self, obj_data: dict):
        obj = Text(**obj_data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, text_id: int):
        return self.session.query(Text).filter_by(text_id=text_id).first()

    def get_all(self):
        return self.session.query(Text).all()

    def update(self, text_id: int, **kwargs):
        text = self.get_by_id(text_id)
        if not text:
            return None
        for key, value in kwargs.items():
            setattr(text, key, value)
        self.session.commit()
        self.session.refresh(text)
        return text

    def delete_by_id(self, text_id: int):
        text = self.get_by_id(text_id)
        if text:
            self.session.delete(text)
            self.session.commit()
            return True
        return False