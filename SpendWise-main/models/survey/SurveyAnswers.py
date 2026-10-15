from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class SurveyAnswer(Base):
    __tablename__ = 'Survey_Answers'
    answer_id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('Satisfaction_Survey.survey_id'), nullable=False)
    question_code = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_value = Column(Integer, nullable=False)  # 1-5

    survey = relationship("SatisfactionSurvey", back_populates="answers")
# SurveyAnswers.py - models
