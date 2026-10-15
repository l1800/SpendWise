from models.Finance.BudgetPlan import BudgetPlan
from repositories.base_repository import BaseRepository


class BudgetPlanRepository(BaseRepository):

    def save_plan_for_month(self, user_id, year, month, plan_dict):
        """
        Deletes any existing plan rows for this user/month,
        then inserts fresh rows from the plan dict produced by
        BudgetBuilderService.build_next_month_budget().
        """
        # ── 1. delete old rows for this user + month ──
        self.session.query(BudgetPlan).filter(
            BudgetPlan.user_id == user_id,
            BudgetPlan.year == year,
            BudgetPlan.month == month
        ).delete()
        self.session.flush()

        # ── 2. insert new rows ──
        budget_items = plan_dict.get("budget", [])
        for item in budget_items:
            row = BudgetPlan(
                user_id=user_id,
                category_id=item["category_id"],
                year=year,
                month=month,
                planned_amount=item.get("planned_amount", 0),
                holiday_adjustment=item.get("holiday_adjustment", 0),
                holiday_name=item.get("holiday_name"),
            )
            self.session.add(row)

        self.session.commit()

    def get_plan_for_month(self, user_id, year, month):
        """Returns list of BudgetPlan rows for a given user + month."""
        return (
            self.session.query(BudgetPlan)
            .filter(
                BudgetPlan.user_id == user_id,
                BudgetPlan.year == year,
                BudgetPlan.month == month
            )
            .all() 
        )
