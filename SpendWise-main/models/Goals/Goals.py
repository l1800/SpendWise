from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base


class Goal(Base):
    __tablename__ = 'Goals'
    goal_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    goal_created_date = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="goals")
    details = relationship("GoalDetail", back_populates="goal")
# Goals.py - models
