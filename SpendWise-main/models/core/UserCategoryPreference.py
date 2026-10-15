from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class UserCategoryPreference(Base):
    __tablename__ = 'User_Category_Preferences'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey('Users.user_id'),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey('Categories.category_id'),
        nullable=False
    )

    importance_score = Column(Float, nullable=False)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================
    # relationships
    # =========================

    user = relationship(
        "User",
        back_populates="category_preferences"
    )

    category = relationship(
        "Category",
        back_populates="user_category_preferences"
    )