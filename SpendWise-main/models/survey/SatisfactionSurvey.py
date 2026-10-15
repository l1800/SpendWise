from sqlalchemy import Column, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class SatisfactionSurvey(Base):
    __tablename__ = 'Satisfaction_Survey'
    survey_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    survey_date = Column(Date, nullable=False)
    feedback = Column(Text)

    user = relationship("User", back_populates="satisfaction_surveys")
    answers = relationship("SurveyAnswer", back_populates="survey")