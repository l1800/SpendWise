from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class UserCategoryGoal(Base):
    """יעד חודשי אידיאלי לכל קטגוריה — מחושב אוטומטית לפי amount_per_person × family_size."""
    __tablename__ = "User_Category_Goal"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("Categories.category_id"),
        nullable=False
    )

    # =========================
    # target_amount = amount_per_person × family_size
    # (מחושב אוטומטית — לא מוזן ידנית)
    # =========================
    target_amount = Column(Float, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # =========================
    # relationships
    # =========================
    user = relationship("User", back_populates="category_goals")
    category = relationship("Category", back_populates="category_goals")
