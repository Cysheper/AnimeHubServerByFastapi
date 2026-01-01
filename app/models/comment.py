"""
数据库模型 - 评论
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post


class Comment(Base):
    """评论模型"""
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # 关系
    author: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    likes: Mapped[list["CommentLike"]] = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")


class CommentLike(Base):
    """评论点赞模型"""
    __tablename__ = "comment_likes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="comment_likes")
    comment: Mapped["Comment"] = relationship("Comment", back_populates="likes")
