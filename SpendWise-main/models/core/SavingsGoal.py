from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class SavingsGoal(Base):
    """יעד חיסכון — המשתמש מחליט לכמה דברים הוא חוסך (דירה, חופשה, ריהוט...)"""
    __tablename__ = "Savings_Goals"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("Categories.category_id"),
        nullable=True
    )

    name = Column(String(100), nullable=False)

    current_balance = Column(Float, nullable=False, default=0)

    target_amount = Column(Float, nullable=True, default=None)

    created_at = Column(DateTime, default=datetime.utcnow)

    # =========================
    # relationships
    # =========================
    user = relationship("User", back_populates="savings_goals")
    transactions = relationship(
        "SavingsTransaction",
        back_populates="goal",
        order_by="SavingsTransaction.date"
    )
    monthly_allocations = relationship(
        "UserSavingGoal",
        back_populates="goal"
    )


class SavingsTransaction(Base):
    """תנועה בחיסכון — הפקדה (חיובי) או משיכה (שלילי)"""
    __tablename__ = "Savings_Transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    goal_id = Column(
        Integer,
        ForeignKey("Savings_Goals.id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)

    description = Column(String(200), nullable=True)

    date = Column(DateTime, default=datetime.utcnow)

    # =========================
    # relationships
    # =========================
    goal = relationship("SavingsGoal", back_populates="transactions")
