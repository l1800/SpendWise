# GoalStatus.py - models
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class GoalStatus(Base):
    __tablename__ = 'Goal_Status'
    status_id = Column(Integer, primary_key=True)
    status_name = Column(String(50), unique=True, nullable=False)

    goal_details = relationship("GoalDetail", back_populates="status")
    goal_expectations = relationship("GoalExpectation", back_populates="status")