from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.base import Base


class UserBudgetProgram(Base):
    """מעקב אחרי תוכנית התקציב ההדרגתית של המשתמש (6 חודשים)"""
    __tablename__ = "User_Budget_Program"

    program_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False,
        unique=True  # כל משתמש = תוכנית אחת פעילה
    )

    phase = Column(
        String(20),
        nullable=False,
        default="learning"
        # "learning" | "gradual" | "completed"
    )

    gradual_months_completed = Column(Integer, nullable=False, default=0)
    # חודשים 2–6 = gradual, סופר כמה חודשי gradual הושלמו (מקסימום 5)

    gradual_start_month = Column(Integer, nullable=True)
    # Year*100 + Month — מתי נכנס ל-gradual

    gradual_end_month = Column(Integer, nullable=True)
    # Year*100 + Month — מתי סיים (graduated)

    status = Column(
        String(20),
        nullable=False,
        default="active"
        # "active" | "completed"
    )

    summary_data = Column(Text, nullable=True)
    # JSON dump של דו"ח הסיכום — נוצר כשהתוכנית מסתיימת

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── relationships ──
    user = relationship("User", back_populates="budget_program")
    program_months = relationship(
        "UserBudgetProgramMonth",
        back_populates="program",
        order_by="UserBudgetProgramMonth.month_number"
    )
