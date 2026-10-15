# GoalTypes.py - models
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class GoalType(Base):
    __tablename__ = 'Goal_Types'
    goal_type_id = Column(Integer, primary_key=True)
    goal_type_name = Column(String(50), nullable=False, unique=True)

    # קשרים לטבלאות שתלויות ב-GoalType
    goal_details = relationship("GoalDetail", back_populates="goal_type")
    goal_expectations = relationship("GoalExpectation", back_populates="goal_type")