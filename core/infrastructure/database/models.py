from datetime import datetime, UTC, date
from typing import Optional

from sqlalchemy import Date, Boolean, JSON, Text
from sqlalchemy import ForeignKey, UniqueConstraint, String, Integer, Column, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserStars(Base):
    __tablename__ = "user_stars"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    count: Mapped[int] = mapped_column(default=1)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    user: Mapped["User"] = relationship(back_populates="stars")


class UserCards(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    theme: Mapped[str]
    title: Mapped[str]
    url: Mapped[str]
    # owner: Mapped["User"] = relationship(back_populates="cards")
    __table_args__ = (UniqueConstraint("user_id", "theme", "title"),)


class UserQuizzes(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quiz_id: Mapped[int]
    title: Mapped[str]
    category: Mapped[str]
    difficulty: Mapped[str]
    total_questions: Mapped[int]
    correct_answers: Mapped[int]
    percentage: Mapped[float]
    stars_earned: Mapped[int]
    completed_at: Mapped[datetime] = mapped_column(default=datetime.now)
    time_spent_seconds: Mapped[int] = mapped_column(default=0)
    hints_used: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_by: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user: Mapped["User"] = relationship(back_populates="quizzes")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None]
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # is_approved: Mapped[bool] = mapped_column(default=False)
    # has_requested_access = Column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    avatar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # q_ok: Mapped[int] = mapped_column(default=0)
    # q_tot: Mapped[int] = mapped_column(default=0)
    # streak: Mapped[int] = mapped_column(default=0)
    # last: Mapped[date | None] = mapped_column(Date, nullable=True)
    # cards: Mapped[list["UserCards"]] = relationship(back_populates="owner", cascade="all,delete")
    quizzes: Mapped[list["UserQuizzes"]] = relationship(back_populates="user", cascade="all,delete")
    stars: Mapped[list["UserStars"]] = relationship(back_populates="user", cascade="all,delete")
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    first_active = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_active = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ThemeSetting(Base):
    __tablename__ = "theme_settings"
    theme: Mapped[str] = mapped_column(String, primary_key=True)
    min_len: Mapped[int] = mapped_column(Integer, nullable=False)


class ThemeStat(Base):
    __tablename__ = "theme_stats"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    theme: Mapped[str] = mapped_column(primary_key=True)
    texts: Mapped[int] = mapped_column(default=0)


class TextGeneration(Base):
    __tablename__ = "text_generations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True, nullable=False)
    theme = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class History(Base):
    __tablename__ = "history"
    hash: Mapped[str] = mapped_column(String, primary_key=True)
