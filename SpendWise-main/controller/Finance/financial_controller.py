from flask import Blueprint, jsonify
from db_connection import SessionLocal
from repositories.Finance.FinancialRepository import FinancialRepository
from services.Finance.FinancialStressService import FinancialStressService
from services.Finance.BehaviorStressService import BehaviorStressService
from services.Finance.FinancialHealthService import FinancialHealthService
from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService

financial_controller = Blueprint("financial", __name__)


@financial_controller.route("/financial/stress/<int:user_id>/<int:year>/<int:month>")
def get_financial_stress(user_id, year, month):

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
