from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base


class GoalDetail(Base):
    __tablename__ = 'Goal_Details'
    detail_id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey('Goals.goal_id'), nullable=False)
    goal_type_id = Column(Integer, ForeignKey('Goal_Types.goal_type_id'), nullable=False)
    goal_description = Column(String, nullable=False)
    goal_target_date = Column(Date, nullable=False)
    status_id = Column(Integer, ForeignKey('Goal_Status.status_id'), nullable=False)
    goal_type = relationship(
        "GoalType",
        back_populates="goal_details"
    )
    goal = relationship("Goal", back_populates="details")
    status = relationship("GoalStatus", back_populates="goal_details")
# GoalDetails.py - models
