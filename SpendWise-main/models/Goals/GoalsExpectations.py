from sqlalchemy import Column, Integer, Date, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base


class GoalExpectation(Base):
    __tablename__ = 'Goals_Expectations'
    expectation_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    goal_type_id = Column(Integer, ForeignKey('Goal_Types.goal_type_id'), nullable=False)
    goal_description = Column(String, nullable=False)
    goal_target_date = Column(Date, nullable=False)
    status_id = Column(Integer, ForeignKey('Goal_Status.status_id'), nullable=False)
    goal_created_date = Column(DateTime, nullable=False)

    user = relationship(
        "User",
        back_populates="goal_expectations"
    )
    goal_type = relationship(
        "GoalType",
        back_populates="goal_expectations"
    )
    status = relationship("GoalStatus", back_populates="goal_expectations")
# GoalsExpectations.py - models
