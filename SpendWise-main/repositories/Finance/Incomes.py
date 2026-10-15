from models.Finance.Incomes import Income
from repositories.base_repository import BaseRepository

class IncomesRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)
        self.model = Income  # כאן אנחנו מגדירים את המודל רק ל-IncomesRepository

    def get_by_id(self, transaction_id):
        return self.session.query(self.model).filter_by(transaction_id=transaction_id).first()

    def get_all(self):
        return self.session.query(self.model).all()

    def update(self, transaction_id, **kwargs):
        item = self.get_by_id(transaction_id)
        if not item:
            return None
        for key, value in kwargs.items():
            setattr(item, key, value)
        self.session.commit()
        return item

    def delete_by_id(self, transaction_id):
        item = self.get_by_id(transaction_id)
        if item:
            self.delete(item)
        return item