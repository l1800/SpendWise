from models.core.Users import User
from repositories.base_repository import BaseRepository
class UserRepository(BaseRepository):

    def get_by_id(self, user_id):
        return self.session.query(User).filter_by(user_id=user_id).first()

    def get_all(self):
        return self.session.query(User).all()

    def exists_by_email(self, email):
        return self.session.query(User).filter_by(email=email).first() is not None

    def update(self, user_id, **kwargs):
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        self.session.commit()
        return user

    def delete_by_id(self, user_id):
        user = self.get_by_id(user_id)
        if user:
            self.delete(user)
        return user