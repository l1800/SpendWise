from flask import Blueprint, jsonify
from db_connection import SessionLocal
from repositories.Finance.BudgetRepository import BudgetRepository
from repositories.Finance.FinancialRepository import FinancialRepository
from services.Finance.budget_service import BudgetService
from services.Finance.FinancialStressService import FinancialStressService
from services.Finance.BehaviorStressService import BehaviorStressService
from services.Finance.FinancialHealthService import FinancialHealthService
from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService

# יצירת Blueprint לנתיבי תקציב
budget_controller = Blueprint("budget", __name__)


# ==========================================
# חישוב תקציב נטו (כמה כסף נשאר למשתמש)
# ==========================================
@budget_controller.route("/budget/net/<int:user_id>/<int:year>/<int:month>")
def get_budget(user_id, year, month):

    # פתיחת חיבור למסד הנתונים
    session = SessionLocal()

    try:
        # יצירת שכבת גישה ל-DB
        repo = BudgetRepository(session)

        # יצירת שכבת לוגיקה עסקית
        service = BudgetService(repo)

        # חישוב תקציב נטו (הכנסות - הוצאות קבועות)
        result = service.calculate_net_budget(user_id, year, month)

        # החזרת תשובה ללקוח בפורמט JSON
        return jsonify(result)

    finally:
        # סגירת חיבור למסד הנתונים כדי לא להשאיר session פתוח
        session.close()


# ==========================================
# הוצאות לפי קטגוריה (חיוני / רצון)
# ==========================================
@budget_controller.route("/budget/expenses-by-category/<int:user_id>/<int:year>/<int:month>")
def get_expenses_by_category(user_id, year, month):

    session = SessionLocal()

    try:
        repo = BudgetRepository(session)
        service = BudgetService(repo)

        result = service.get_monthly_expenses_by_category(user_id, year, month)

        return jsonify(result)

    finally:
        session.close()


@budget_controller.route("/budget/standard/<int:family_size>")
def get_standard_budget(family_size):

    session = SessionLocal()

    try:
        repo = BudgetRepository(session)
        service = BudgetService(repo)

        result = service.get_standard_budget(family_size)

        return jsonify(result)

    finally:
        session.close()


@budget_controller.route("/budget/stress/<int:user_id>/<int:year>/<int:month>")
def get_stress(user_id, year, month):

    session = SessionLocal()

    try:
        repo = FinancialRepository(session)
        monthly_service = MonthlyExpensesSummaryService(repo)
        spike_service = FinancialStressService(repo, None)
        behavior_service = BehaviorStressService(repo, monthly_service)
        service = FinancialHealthService(spike_service, behavior_service, repo)

        result = service.calculate_financial_score(user_id, year, month)

        return jsonify(result)

    finally:
        session.close()
