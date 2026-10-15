from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler

from db_connection import SessionLocal

from repositories.core.Users import UserRepository
from repositories.Finance.BudgetPlanRepository import BudgetPlanRepository
from repositories.Finance.BudgetRepository import BudgetRepository
from repositories.core.UserCategoryPreferenceRepository import UserCategoryPreferenceRepository
from repositories.core.CategoryStandard import CategoryStandardRepository
from repositories.system.MonthlyExpensesSummary import MonthlyExpensesSummaryRepository
from repositories.system.EarlyWarningAlert import EarlyWarningAlertRepository
from repositories.system.SpecialPeriodSummary import SpecialPeriodSummaryRepository
from repositories.core.UserCategoryGoalRepository import UserCategoryGoalRepository
from repositories.core.UserSavingGoalRepository import UserSavingGoalRepository

from services.Finance.budget_service import BudgetService
from services.Finance.EarlyWarningService import EarlyWarningService
from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService
from services.system.SpecialPeriodSummary import SpecialPeriodService
from services.Finance.GradualBudgetService import GradualBudgetService
from services.Finance.CategoryBehaviorService import CategoryBehaviorService
from services.Finance.BehaviorStressService import BehaviorStressService
from services.Finance.HolidayAdjustmentService import HolidayAdjustmentService
from services.core.UserSavingGoalService import UserSavingGoalService


def _build_services(session):
    """בונה את כל ה-services וה-repositories ל-session נתון."""
    user_repo = UserRepository(session)
    budget_repo = BudgetRepository(session)
    preference_repo = UserCategoryPreferenceRepository(session)
    standard_repo = CategoryStandardRepository(session)
    monthly_repo = MonthlyExpensesSummaryRepository(session)
    special_period_repo = SpecialPeriodSummaryRepository(session)
    special_period_service = SpecialPeriodService(special_period_repo)
    alert_repo = EarlyWarningAlertRepository(session)
    plan_repo = BudgetPlanRepository(session)
    user_goal_repo = UserCategoryGoalRepository(session)
    saving_goal_repo = UserSavingGoalRepository(session)

    budget_service = BudgetService(budget_repo)
    monthly_service = MonthlyExpensesSummaryService(monthly_repo, special_period_service)
    behavior_stress = BehaviorStressService(monthly_repo, monthly_service)
    category_behavior = CategoryBehaviorService()
    holiday_adjustment = HolidayAdjustmentService(session)
    early_warning = EarlyWarningService(session, alert_repo)
    saving_goal_service = UserSavingGoalService(saving_goal_repo)

    gradual_service = GradualBudgetService(
        session=session,
        budget_service=budget_service,
        monthly_analysis_service=monthly_service,
        behavior_stress_service=behavior_stress,
        category_behavior_service=category_behavior,
        holiday_adjustment_service=holiday_adjustment,
        special_period_service=special_period_service,
        budget_plan_repository=plan_repo,
        user_goal_repo=user_goal_repo,
        preference_repo=preference_repo,
        standard_repo=standard_repo,
    )

    return gradual_service, plan_repo, saving_goal_service


def generate_monthly_budgets():
    session_obj = None
    try:
        print("MONTHLY BUDGET JOB STARTED")
        session_obj = SessionLocal()

        today = date.today()
        target_year = today.year
        target_month = today.month

        user_repo = UserRepository(session_obj)
        users = user_repo.get_all()

        for user in users:
            try:
                gradual_service, plan_repo, saving_goal_service = _build_services(session_obj)

                # ======================================================
                # שלב 1 — בניית תוכנית תקציבית
                # ======================================================
                plan = gradual_service.build_plan(
                    user_id=user.user_id,
                    year=target_year,
                    month=target_month
                )

                # ======================================================
                # שלב 2 — חלוקת חסכון לפי User_Saving_Goal
                # ======================================================
                saved_this_month = plan.get("saved_this_month", 0)

                if saved_this_month > 0:
                    allocations = saving_goal_service.allocate_savings(
                        user_id=user.user_id,
                        total_savings=saved_this_month
                    )

                    # שמירת סכומי החיסכון המחולקים ב-Budget_Plans
                    # (הקטגוריות של החיסכון הן קטגוריות רגילות — category_id 11 = חסכונות והשקעות, וכו')
                    for alloc in allocations:
                        if alloc["amount"] > 0:
                            plan_repo.save_plan_for_month(
                                user_id=user.user_id,
                                year=target_year,
                                month=target_month,
                                plan={
                                    "budget": [{
                                        "category_id": alloc["category_id"],
                                        "category_name": f"saving_{alloc['category_id']}",
                                        "planned_amount": alloc["amount"],
                                        "cut_amount": 0,
                                        "cut_percent": 0,
                                        "is_essential": False,
                                        "is_fixed_cost": False,
                                        "pain_level": 0,
                                        "status": "savings",
                                    }],
                                    "planned_spending": alloc["amount"],
                                    "total_cut_needed": 0,
                                    "actual_cut": 0,
                                    "net_budget": saved_this_month,
                                    "monthly_limit": saved_this_month,
                                }
                            )

                    print(
                        f"Savings distributed for user {user.user_id}: "
                        f"{saved_this_month} NIS → {len(allocations)} categories"
                    )

                # ======================================================
                # שלב 3 — בדיקת סיום תוכנית + הפקת דו"ח סיכום
                # ======================================================
                program_phase = plan.get("program_phase", "")
                if program_phase == "maintenance":
                    program_month = plan.get("program_month", 0)
                    print(
                        f"User {user.user_id} program COMPLETED "
                        f"(month {program_month}) — generating summary"
                    )
                    # Generate and print summary
                    summary = gradual_service.generate_program_summary(user.user_id)
                    if "error" not in summary:
                        print(
                            f"SUMMARY: savings={summary.get('total_savings', 0):,.0f}₪ "
                            f"({summary.get('savings_percent', 0)}%), "
                            f"verdict: {summary.get('overall_verdict', '')}"
                        )
                    else:
                        print(f"Summary skipped: {summary.get('error')}")

                print(f"Created budget for user {user.user_id} {target_year}-{target_month}")

            except Exception as e:
                print(f"ERROR creating budget for user {user.user_id}: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"MONTHLY BUDGET JOB FAILED: {e}")
    finally:
        if session_obj:
            session_obj.close()
            print("DATABASE SESSION CLOSED")


scheduler = BackgroundScheduler()
scheduler.add_job(
    func=generate_monthly_budgets,
    trigger="cron",
    day=1,
    hour=2,
    minute=0
)
scheduler.start()
print("MONTHLY BUDGET SCHEDULER STARTED — runs on the 1st of each month at 02:00")
