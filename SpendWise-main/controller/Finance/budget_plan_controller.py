from flask import Blueprint, jsonify, request
from datetime import date
from db_connection import SessionLocal

from services.Finance.BudgetPlanService import BudgetPlanService
from services.Finance.budget_service import BudgetService
from services.Finance.CutRankingService import CutRankingService
from services.Finance.CutAllocationService import CutAllocationService
from services.Finance.BudgetBuilderService import BudgetBuilderService
from services.Finance.EarlyWarningService import EarlyWarningService
from services.system.RecommendationTextService import RecommendationTextService
from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService

from repositories.Finance.BudgetRepository import BudgetRepository
from repositories.core.UserCategoryPreferenceRepository import UserCategoryPreferenceRepository
from repositories.core.CategoryStandard import CategoryStandardRepository
from repositories.core.UserSavingGoalRepository import UserSavingGoalRepository
from repositories.system.MonthlyExpensesSummary import MonthlyExpensesSummaryRepository
from repositories.system.EarlyWarningAlert import EarlyWarningAlertRepository
from repositories.Finance.BudgetPlanRepository import BudgetPlanRepository
from repositories.Finance.FinancialRepository import FinancialRepository
from repositories.core.Users import UserRepository
from services.Finance.FinancialStressService import FinancialStressService
from services.Finance.BehaviorStressService import BehaviorStressService
from services.Finance.FinancialHealthService import FinancialHealthService

budget_plan_controller = Blueprint("budget_plan", __name__)
@budget_plan_controller.route("/test-budget", methods=["GET"])
def test_budget():
    return jsonify({
        "status": "ok"
    })

def _build_service(session):
    """Constructs BudgetPlanService with all dependencies wired."""
    budget_repo = BudgetRepository(session)
    preference_repo = UserCategoryPreferenceRepository(session)
    standard_repo = CategoryStandardRepository(session)
    saving_repo = UserSavingGoalRepository(session)
    monthly_repo = MonthlyExpensesSummaryRepository(session)
    alert_repo = EarlyWarningAlertRepository(session)
    plan_repo = BudgetPlanRepository(session)

    budget_service = BudgetService(budget_repo)
    analysis_service = MonthlyExpensesSummaryService(monthly_repo)
    financial_repo = FinancialRepository(session)
    financial_health_service = FinancialHealthService(
        FinancialStressService(financial_repo, analysis_service),
        BehaviorStressService(financial_repo, analysis_service),
        financial_repo
    )
    user_repo = UserRepository(session)

    ranking_service = CutRankingService(
        budget_service=budget_service,
        preference_repo=preference_repo,
        standard_repo=standard_repo,
        analysis_service=analysis_service
    )

    allocation_service = CutAllocationService(
        budget_service=budget_service,
        saving_repo=saving_repo,
        standard_repo=standard_repo
    )

    early_warning_service = EarlyWarningService(
        session=session,
        alert_repo=alert_repo
    )

    return BudgetPlanService(
        budget_service=budget_service,
        cut_ranking_service=ranking_service,
        cut_allocation_service=allocation_service,
        builder_service=BudgetBuilderService(),
        recommendation_service=RecommendationTextService(),
        early_warning_service=early_warning_service,
        budget_plan_repository=plan_repo,
        financial_health_service=financial_health_service,
        user_repository=user_repo
    ), plan_repo, early_warning_service


# ── build plan (existing) ──

@budget_plan_controller.route("/budget/plan/<int:user_id>/<int:year>/<int:month>")
def get_budget_plan_route(user_id, year, month):
    session = SessionLocal()
    try:
        svc, _, _ = _build_service(session)
        result = svc.build_plan(user_id=user_id, year=year, month=month)
        return jsonify(result), 200
    except Exception as ex:
        session.rollback()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── status: what the user sees mid-month ──

@budget_plan_controller.route("/budget/status", methods=["GET"])
def get_budget_status():
    """
    Returns "how much did I spend in each category out of my planned budget"
    for the current month, plus any active EarlyWarning alerts.
    """
    user_id = request.args.get("user_id", type=int)

    # defaults to current year/month
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    session = SessionLocal()
    try:
        _, plan_repo, early_warning_service = _build_service(session)

        # 1. load saved plan
        plan_rows = plan_repo.get_plan_for_month(user_id, year, month)

        if not plan_rows:
            return jsonify({
                "success": False,
                "message": f"No budget plan found for {year}-{month}. "
                           f"Run POST /budget/plan first."
            }), 404

        # rebuild the plan dict shape that check_spending_vs_budget expects
        plan_dict = {
            "monthly_limit": sum(r.planned_amount for r in plan_rows),
            "budget": [
                {
                    "category_id": r.category_id,
                    "planned_amount": r.planned_amount,
                    "category_name": r.category.category_name if r.category else "",
                }
                for r in plan_rows
            ]
        }

        # 2. run early warning check (returns spending status per category)
        warning_result = early_warning_service.check_spending_vs_budget(
            user_id, year, month, plan_dict
        )

        return jsonify({
            "year": year,
            "month": month,
            "monthly_limit": plan_dict["monthly_limit"],
            "status": warning_result,
        }), 200

    except Exception as ex:
        session.rollback()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── view raw Budget_Plans data ──

@budget_plan_controller.route("/budget/plans", methods=["GET"])
def get_budget_plans_data():
    """
    Returns raw data from Budget_Plans table.
    Use: GET /budget/plans?user_id=1&year=2026&month=7
    """
    user_id = request.args.get("user_id", type=int)
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    session = SessionLocal()
    try:
        _, plan_repo, _ = _build_service(session)
        rows = plan_repo.get_plan_for_month(user_id, year, month)
        raise Exception("TEST ROUTE")
        print("USER:", user_id)
        print("YEAR:", year)
        print("MONTH:", month)
        print("ROWS:", len(rows))
        return jsonify({
            "year": year,
            "month": month,
            "count": len(rows),
            "plans": [
                {
                    "plan_id": r.plan_id,
                    "user_id": r.user_id,
                    "category_id": r.category_id,
                    "planned_amount": r.planned_amount,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ]
        }), 200

    except Exception as ex:
        session.rollback()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()
