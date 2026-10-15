from typing import List, Optional

from models.survey.SatisfactionSurvey import SatisfactionSurvey
from repositories.base_repository import BaseRepository
from dto.survey.SatisfactionSurveyDto import SatisfactionSurveyCreateDTO


class SatisfactionSurveyRepository(BaseRepository):

    def get_by_id(self, survey_id: int) -> Optional[SatisfactionSurvey]:
        return (
            self.session.query(SatisfactionSurvey)
            .filter(SatisfactionSurvey.survey_id == survey_id)
            .first()
        )

    def get_by_user(self, user_id: int) -> List[SatisfactionSurvey]:
        return (
            self.session.query(SatisfactionSurvey)
            .filter(SatisfactionSurvey.user_id == user_id)
            .all()
        )

    def get_all(self) -> List[SatisfactionSurvey]:
        return self.session.query(SatisfactionSurvey).all()

    def create(self, dto: SatisfactionSurveyCreateDTO) -> SatisfactionSurvey:
        survey = SatisfactionSurvey(
            user_id=dto.user_id,
            survey_date=dto.survey_date,
            feedback=dto.feedback
        )

        self.session.add(survey)
        self.session.commit()
        self.session.refresh(survey)
        return survey

    def update(self, survey_id: int, **kwargs) -> Optional[SatisfactionSurvey]:
        survey = self.get_by_id(survey_id)

        if not survey:
            return None

        for key, value in kwargs.items():
            if hasattr(survey, key):
                setattr(survey, key, value)

        self.session.commit()
        self.session.refresh(survey)
        return survey

    def delete_by_id(self, survey_id: int) -> bool:
        survey = self.get_by_id(survey_id)

        if not survey:
            return False

        self.session.delete(survey)
        self.session.commit()
        return True