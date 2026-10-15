from repositories.system.Recommendations import RecommendationRepository
from dto.system.RecommendationsDto import RecommendationCreateDTO, RecommendationResponseDTO


class RecommendationService:

    def __init__(self, repository: RecommendationRepository):
        self.repository = repository

    def create(self, dto: RecommendationCreateDTO):
        return self.repository.create(dto.dict())

    def get_by_id(self, recommendation_id: int):
        return self.repository.get_by_id(recommendation_id)

    def get_all(self):
        return self.repository.get_all()

    def get_by_user(self, user_id: int):
        return self.repository.get_by_user(user_id)

    def update(self, recommendation_id: int, **kwargs):
        return self.repository.update(recommendation_id, **kwargs)

    def delete(self, recommendation_id: int):
        return self.repository.delete_by_id(recommendation_id)