from flask import Blueprint, request, jsonify
from dto.survey.SatisfactionSurveyDto import (
    SatisfactionSurveyCreateDTO,
    SatisfactionSurveyResponseDTO
)
from services.survey.SatisfactionSurvey import SatisfactionSurveyService
from repositories.survey.SatisfactionSurvey import SatisfactionSurveyRepository
from db_connection import SessionLocal

satisfaction_survey_blueprint = Blueprint(
    'satisfaction_survey',
    __name__,
    url_prefix='/satisfaction-survey'
)

def get_service():
    session = SessionLocal()
    repo = SatisfactionSurveyRepository(session)
    service = SatisfactionSurveyService(repo)
    return session, service

# ==================== יצירה ====================
@satisfaction_survey_blueprint.route('/', methods=['POST'])
def create_survey():
    session, service = get_service()
    try:
        dto = SatisfactionSurveyCreateDTO(**request.get_json())
        survey = service.create(dto)
        return jsonify({"survey_id": survey.survey_id}), 201
    finally:
        session.close()

# ==================== קבלת הכל ====================
@satisfaction_survey_blueprint.route('/', methods=['GET'])
def get_all_surveys():
    session, service = get_service()
    try:
        surveys = service.get_all()
        return jsonify([
            SatisfactionSurveyResponseDTO.model_validate(s).model_dump(mode="json")
            for s in surveys
        ])
    finally:
        session.close()

# ==================== קבלת לפי ID ====================
@satisfaction_survey_blueprint.route('/<int:survey_id>', methods=['GET'])
def get_survey(survey_id):
    session, service = get_service()
    try:
        survey = service.get_by_id(survey_id)
        if not survey:
            return jsonify({"error": "Survey not found"}), 404
        return jsonify(
            SatisfactionSurveyResponseDTO.model_validate(survey).model_dump(mode="json")
        )
    finally:
        session.close()

# ==================== עדכון ====================
@satisfaction_survey_blueprint.route('/<int:survey_id>', methods=['PUT'])
def update_survey(survey_id):
    session, service = get_service()
    try:
        feedback = request.get_json().get("feedback")
        survey = service.update(survey_id, feedback)
        if not survey:
            return jsonify({"error": "Survey not found"}), 404
        return jsonify({"message": "Survey updated"})
    finally:
        session.close()

# ==================== מחיקה ====================
@satisfaction_survey_blueprint.route('/<int:survey_id>', methods=['DELETE'])
def delete_survey(survey_id):
    session, service = get_service()
    try:
        success = service.delete(survey_id)
        if not success:
            return jsonify({"error": "Survey not found"}), 404
        return jsonify({"message": "Survey deleted"})
    finally:
        session.close()