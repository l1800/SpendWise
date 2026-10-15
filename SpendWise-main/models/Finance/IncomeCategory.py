# models/Finance/IncomeCategories.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class IncomeCategory(Base):
    __tablename__ = "IncomeCategories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False)

    # רשימת הכנסות ששייכות לקטגוריה
    incomes = relationship("Income", back_populates="category")