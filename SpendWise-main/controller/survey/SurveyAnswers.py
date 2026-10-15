from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from dto.survey.SurveyAnswersDto import (
    SurveyAnswerCreateDTO,
    SurveyAnswerResponseDTO
)
from services.survey.SurveyAnswers import SurveyAnswersService
from repositories.survey.SurveyAnswers import SurveyAnswersRepository
from db_connection import SessionLocal

survey_answers_blueprint = Blueprint(
    'survey_answers',
    __name__,
    url_prefix='/survey-answers'
)

def get_service():
    session: Session = SessionLocal()
    repo = SurveyAnswersRepository(session)
    service = SurveyAnswersService(repo)
    return session, service

# ==================== יצירה ====================
@survey_answers_blueprint.route('/', methods=['POST'])
def create_answer():
    session, service = get_service()
    try:
        dto = SurveyAnswerCreateDTO(**request.get_json())
        answer = service.create(dto)
        return jsonify(SurveyAnswerResponseDTO.model_validate(answer).model_dump(mode="json")), 201
    finally:
        session.close()

# ==================== קבלת הכל ====================
@survey_answers_blueprint.route('/', methods=['GET'])
def get_all_answers():
    session, service = get_service()
    try:
        answers = service.get_all()
        return jsonify([
            SurveyAnswerResponseDTO.model_validate(a).model_dump(mode="json")
            for a in answers
        ])
    finally:
        session.close()

# ==================== קבלת לפי ID ====================
@survey_answers_blueprint.route('/<int:answer_id>', methods=['GET'])
def get_answer_by_id(answer_id):
    session, service = get_service()
    try:
        answer = service.get_by_id(answer_id)
        if not answer:
            return jsonify({"error": "Answer not found"}), 404
        return jsonify(SurveyAnswerResponseDTO.model_validate(answer).model_dump(mode="json"))
    finally:
        session.close()

# ==================== קבלת לפי סקר ====================
@survey_answers_blueprint.route('/survey/<int:survey_id>', methods=['GET'])
def get_answers_by_survey(survey_id):
    session, service = get_service()
    try:
        answers = service.get_by_survey(survey_id)
        return jsonify([
            SurveyAnswerResponseDTO.model_validate(a).model_dump(mode="json")
            for a in answers
        ])
    finally:
        session.close()

# ==================== עדכון ====================
@survey_answers_blueprint.route('/<int:answer_id>', methods=['PUT'])
def update_answer(answer_id):
    session, service = get_service()
    try:
        answer_value = request.get_json().get("answer_value")
        answer = service.update(answer_id, answer_value)
        if not answer:
            return jsonify({"error": "Answer not found"}), 404
        return jsonify(SurveyAnswerResponseDTO.model_validate(answer).model_dump(mode="json"))
    finally:
        session.close()

# ==================== מחיקה ====================
@survey_answers_blueprint.route('/<int:answer_id>', methods=['DELETE'])
def delete_answer(answer_id):
    session, service = get_service()
    try:
        success = service.delete(answer_id)
        if not success:
            return jsonify({"error": "Answer not found"}), 404
        return jsonify({"success": True})
    finally:
        session.close()