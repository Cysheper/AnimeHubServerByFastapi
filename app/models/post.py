"""
数据库模型 - 帖子
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timezone import now_beijing

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.comment import Comment


class Post(Base):
    """帖子模型"""
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    images: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_beijing
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_beijing,
        onupdate=now_beijing
    )
    
    # 关系
    author: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[list["PostLike"]] = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    favorites: Mapped[list["PostFavorite"]] = relationship("PostFavorite", back_populates="post", cascade="all, delete-orphan")


class PostLike(Base):
    """帖子点赞模型"""
    __tablename__ = "post_likes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_beijing
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="post_likes")
    post: Mapped["Post"] = relationship("Post", back_populates="likes")


class PostFavorite(Base):
    """帖子收藏模型"""
    __tablename__ = "post_favorites"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_beijing
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    post: Mapped["Post"] = relationship("Post", back_populates="favorites")
