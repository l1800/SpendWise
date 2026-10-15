from typing import List, Optional
from dto.survey.SatisfactionSurveyDto import SatisfactionSurveyCreateDTO
from models.survey.SatisfactionSurvey import SatisfactionSurvey
from repositories.survey.SatisfactionSurvey import SatisfactionSurveyRepository

class SatisfactionSurveyService:

    def __init__(self, repo: SatisfactionSurveyRepository):
        self.repo = repo

    def create(self, dto: SatisfactionSurveyCreateDTO) -> SatisfactionSurvey:
        survey = SatisfactionSurvey(
            user_id=dto.user_id,
            survey_date=dto.survey_date,
            feedback=dto.feedback
        )
        return self.repo.add(survey)

    def get_all(self) -> List[SatisfactionSurvey]:
        return self.repo.get_all()

    def get_by_id(self, survey_id: int) -> Optional[SatisfactionSurvey]:
        return self.repo.get_by_id(survey_id)

    def get_by_user(self, user_id: int) -> List[SatisfactionSurvey]:
        return self.repo.get_by_user(user_id)

    def update(self, survey_id: int, feedback: str) -> Optional[SatisfactionSurvey]:
        survey = self.repo.get_by_id(survey_id)
        if not survey:
            return None
        survey.feedback = feedback
        return self.repo.update(survey)

    def delete(self, survey_id: int) -> bool:
        return self.repo.delete_by_id(survey_id)