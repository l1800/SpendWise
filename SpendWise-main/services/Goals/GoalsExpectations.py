# services/goals_expectations_service.py
from dto.Goals.GoalsDto import GoalCreateDTO
from repositories.Goals.GoalsExpectations import GoalsExpectationsRepository
from models.Goals.GoalsExpectations import GoalExpectation


class GoalsExpectationsService:
    def __init__(self, repo: Goals):
        self.repo = repo

    def create_expectation(self, dto: GoalsExpectationsDto):
        expectation = GoalExpectation(
            user_id=dto.user_id,
            goal_type_id=dto.goal_type_id,
            goal_description=dto.goal_description,
            goal_target_date=dto.goal_target_date,
            status_id=dto.status_id,
            goal_created_date=dto.goal_created_date
        )
        self.repo.add(expectation)
        return expectation

    def get_all_expectations(self):
        return self.repo.get_all()

    def get_expectations_by_user(self, user_id: int):
        return self.repo.get_by_user(user_id)

    def get_expectation_by_id(self, expectation_id: int):
        return self.repo.get_by_id(expectation_id)

    def update_expectation(self, expectation_id: int, dto: GoalsExpectationsDto):
        return self.repo.update(
            expectation_id,
            user_id=dto.user_id,
            goal_type_id=dto.goal_type_id,
            goal_description=dto.goal_description,
            goal_target_date=dto.goal_target_date,
            status_id=dto.status_id,
            goal_created_date=dto.goal_created_date
        )

    def delete_expectation(self, expectation_id: int):
        return self.repo.delete_by_id(expectation_id)
