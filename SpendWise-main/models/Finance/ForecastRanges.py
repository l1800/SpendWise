from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class ForecastRange(Base):
    __tablename__ = 'Forecast_Ranges'
    range_id = Column(Integer, primary_key=True)
    range_name = Column(String(50), unique=True, nullable=False)

    financial_forecasts = relationship("FinancialForecast", back_populates="range")