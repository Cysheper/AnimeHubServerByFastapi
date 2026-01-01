"""
数据库模型 - 用户
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Boolean, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.post import Post, PostLike, PostFavorite
    from app.models.comment import Comment, CommentLike


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 通知设置
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    message_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    public_profile: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # 关系
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    post_likes: Mapped[list["PostLike"]] = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    comment_likes: Mapped[list["CommentLike"]] = relationship("CommentLike", back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[list["PostFavorite"]] = relationship("PostFavorite", back_populates="user", cascade="all, delete-orphan")
    
    # 关注关系
    following: Mapped[list["Follow"]] = relationship(
        "Follow", 
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    followers: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.following_id", 
        back_populates="following",
        cascade="all, delete-orphan"
    )
    
    def get_avatar_url(self) -> str:
        """获取头像URL"""
        if self.avatar:
            return self.avatar
        return f"https://api.dicebear.com/7.x/avataaars/svg?seed={self.username}"


class Follow(Base):
    """关注关系模型"""
    __tablename__ = "follows"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # 关系
    follower: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[follower_id],
        back_populates="following"
    )
    following: Mapped["User"] = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers"
    )
