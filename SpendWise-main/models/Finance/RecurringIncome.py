from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from models.base import Base


class RecurringIncome(Base):
    """
    הכנסה חוזרת — המשתמש מכניס פעם אחת, והמערכת מחשבת אותה כל חודש.
    """
    __tablename__ = "Recurring_Incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("IncomeCategories.category_id"),
        nullable=False
    )

    source_name = Column(String(100), nullable=True)

    amount = Column(Float, nullable=False)

    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
