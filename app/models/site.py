"""
站点数据模型 - 运势和开发者信息
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Fortune(Base):
    """运势模型"""
    __tablename__ = "fortunes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # great, good, normal, bad
    icon: Mapped[str] = mapped_column(String(10), nullable=False)


class Developer(Base):
    """开发者信息模型"""
    __tablename__ = "developers"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class UserFortune(Base):
    """用户运势记录模型 - 记录用户每天抽取的运势"""
    __tablename__ = "user_fortunes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    fortune_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
