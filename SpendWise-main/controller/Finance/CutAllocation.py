from flask import Blueprint, request, jsonify
from db_connection import SessionLocal

from services.Finance.CutAllocationService import CutAllocationService
from services.Finance.budget_service import BudgetService  # חייב להיות קיים

cut_blueprint = Blueprint("cut", __name__, url_prefix="/cut")


def get_service():
    session = SessionLocal()

    budget_service = BudgetService(session)
    cut_service = CutAllocationService(budget_service)

    return session, cut_service


@cut_blueprint.route('/allocate', methods=['POST'])
def allocate_cuts():

    session, service = get_service()

    try:
        data = request.get_json()

        ranking = data["ranking"]
        net_budget = data["net_budget"]
        stress_score = data["stress_score"]
        last_deficit = data["last_deficit"]

        total_cut = service.calculate_total_cut_needed(
            ranking,
            net_budget,
            stress_score,
            last_deficit
        )

        result = service.allocate_cuts(ranking, total_cut)

        return jsonify({
            "total_cut_needed": total_cut,
            "result": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        session.close()