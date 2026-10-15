from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from models.base import Base


class UserSavingGoal(Base):
    """
    הקצאת חיסכון חודשית — המשתמש קובע בתחילת כל חודש
    כמה מהחיסכון החודשי יועבר לכל יעד חיסכון (Savings_Goals).

    נוצר אוטומטית בתחילת חודש (job), המשתמש מעדכן סכומים,
    ואז הסכומים מתווספים ל-Savings_Goals.current_balance.
    """
    __tablename__ = "User_Saving_Goal"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False
    )

    goal_id = Column(
        Integer,
        ForeignKey("Savings_Goals.id"),
        nullable=False
    )

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # הסכום שהמשתמש הקצה ליעד זה החודש
    allocated_amount = Column(Float, nullable=False, default=0)

    # בוצע? (אחרי שהכסף עבר ל-Savings_Transactions)
    applied = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user = relationship("User", back_populates="monthly_savings")
    goal = relationship("SavingsGoal", back_populates="monthly_allocations")
