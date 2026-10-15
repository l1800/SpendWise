from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from models.base import Base
from sqlalchemy.orm import relationship

class EarlyWarningAlert(Base):
    __tablename__ = "EarlyWarning_Alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True)

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

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    alert_type = Column(String(30), nullable=False)
    severity = Column(String(10), nullable=False)

    title = Column(String(200), nullable=False)
    message = Column(Text)

    budget_amount = Column(Float)
    spent_so_far = Column(Float)

    status = Column(String(20), nullable=False, default="ACTIVE")

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    resolved_at = Column(DateTime)

    category = relationship(
        "Category",
        back_populates="early_warning_alerts"
    )

    user = relationship(
        "User",
        back_populates="early_warning_alerts"
    )