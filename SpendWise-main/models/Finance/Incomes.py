from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Income(Base):
    __tablename__ = 'Incomes'
    transaction_id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)

    # סכום הכנסה
    amount = Column(Float, nullable=False)  # <-- כאן השתמשנו ב־Float של SQLAlchemy

    # קשר לקטגוריה
    category_id = Column(Integer, ForeignKey("IncomeCategories.category_id"), nullable=False)
    category = relationship("IncomeCategory", back_populates="incomes")

    # קשר למשתמש
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    user = relationship("User", back_populates="incomes")

    # קשר לתדירות הכנסה
    frequency_id = Column(Integer, ForeignKey("Income_Frequency.frequency_id"), nullable=False)
    frequency = relationship("IncomeFrequency", back_populates="incomes")