from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class IncomeFrequency(Base):
    __tablename__ = 'Income_Frequency'
    frequency_id = Column(Integer, primary_key=True)
    frequency_name = Column(String(50), unique=True, nullable=False)

    incomes = relationship("Income", back_populates="frequency")