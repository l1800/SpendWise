from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from models.base import Base

class SpecialExpense(Base):
    __tablename__ = "Special_Expenses"

    special_expense_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    category_id = Column(Integer, ForeignKey("Categories.category_id"))
    special_date_id = Column(Integer, ForeignKey("Special_Dates.type_id"))
    total_amount = Column(Integer)
    created_at = Column(DateTime)

    user = relationship("User", back_populates="special_expenses")
    category = relationship("Category", back_populates="special_expenses")