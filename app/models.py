from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .database import Base


class User(Base):

    __tablename__ = "users"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True
    )


    username: Mapped[str] = mapped_column(
        String(120)
    )


    age: Mapped[int] = mapped_column(
        Integer
    )


    weight: Mapped[float] = mapped_column(
        Float
    )


    goal: Mapped[str] = mapped_column(
        String(80)
    )


    intensity: Mapped[str] = mapped_column(
        String(20)
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


    plans: Mapped[list["WorkoutPlan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )



class WorkoutPlan(Base):

    __tablename__ = "workout_plans"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        index=True
    )


    original_plan: Mapped[str] = mapped_column(
        Text
    )


    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


    nutrition_tip: Mapped[str] = mapped_column(
        Text
    )


    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


    user: Mapped[User] = relationship(
        back_populates="plans"
    )