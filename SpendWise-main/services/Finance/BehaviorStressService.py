from services.Finance.CategoryBehaviorService import CategoryBehaviorService
from services.Finance.CategoryBehaviorService import CategoryBehaviorService

class BehaviorStressService:

    def __init__(self, repo, monthly_service):
        self.repo = repo
        self.monthly_service = monthly_service
        self.category_service = CategoryBehaviorService()

    def get_data(self, user_id, year, month):
        return self.monthly_service.calculate_category_analysis(user_id, year, month)

    def calculate_behavior_stress(self, user_id, year, month):

        data = self.get_data(user_id, year, month)
        categories = data.get("categories", [])

        if not categories:
            return {"behavior_stress": 0}

        total = 0
        weight_sum = 0

        for c in categories:

            monthly = c.get("monthly_change_percent", 0)
            long_term = c.get("long_term_change_percent", 0)
            essential = c.get("is_essential", False)

            category_score = self.category_service.calculate_category_behavior(
                monthly,
                long_term,
                essential
            )

            weight = abs(monthly) + abs(long_term) + 1

            total += category_score * weight
            weight_sum += weight

        final_score = total / weight_sum if weight_sum else 0

        return {
            "behavior_stress": max(0, min(100, int(final_score)))
        }