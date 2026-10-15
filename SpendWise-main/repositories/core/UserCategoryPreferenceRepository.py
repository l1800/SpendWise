from models.core.UserCategoryPreference import UserCategoryPreference
from repositories.base_repository import BaseRepository


class UserCategoryPreferenceRepository(BaseRepository):

    def upsert(self, dto):

        pref = (
            self.session.query(UserCategoryPreference)
            .filter_by(
                user_id=dto.user_id,
                category_id=dto.category_id
            )
            .first()
        )

        if pref:
            pref.importance_score = dto.importance_score
        else:
            pref = UserCategoryPreference(
                user_id=dto.user_id,
                category_id=dto.category_id,
                importance_score=dto.importance_score
            )
            self.session.add(pref)

        self.session.commit()
        return pref

    def get_by_user(self, user_id):

        return (
            self.session.query(UserCategoryPreference)
            .filter_by(user_id=user_id)
            .all()
        )

    def get_by_user_and_category(self, user_id, category_id):

        return (
            self.session.query(UserCategoryPreference)
            .filter_by(
                user_id=user_id,
                category_id=category_id
            )
            .first()
        )

    def get_all(self):
        return self.session.query(UserCategoryPreference).all()