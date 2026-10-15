from typing import List, Optional

from dto.survey.SurveyAnswersDto import (
    SurveyAnswerCreateDTO,
    SurveyAnswerResponseDTO
)
from repositories.survey.SurveyAnswers import SurveyAnswersRepository


class SurveyAnswersService:

    def __init__(self, repository: SurveyAnswersRepository):
        self.repository = repository

    def get_by_id(self, answer_id: int) -> Optional[SurveyAnswerResponseDTO]:
        obj = self.repository.get_by_id(answer_id)
        return SurveyAnswerResponseDTO.model_validate(obj) if obj else None

    def get_all(self) -> List[SurveyAnswerResponseDTO]:
        return [
            SurveyAnswerResponseDTO.model_validate(answer)
            for answer in self.repository.get_all()
        ]

    def get_by_survey(self, survey_id: int) -> List[SurveyAnswerResponseDTO]:
        return [
            SurveyAnswerResponseDTO.model_validate(answer)
            for answer in self.repository.get_by_survey(survey_id)
        ]

    def create(self, dto: SurveyAnswerCreateDTO) -> SurveyAnswerResponseDTO:
        obj = self.repository.create(dto)
        return SurveyAnswerResponseDTO.model_validate(obj)

    def update(
        self,
        answer_id: int,
        answer_value: int
    ) -> Optional[SurveyAnswerResponseDTO]:

        obj = self.repository.update(
            answer_id,
            answer_value=answer_value
        )

        return SurveyAnswerResponseDTO.model_validate(obj) if obj else None

    def delete(self, answer_id: int) -> bool:
        return self.repository.delete_by_id(answer_id)