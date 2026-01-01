"""
评论相关Schema
"""
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class CommentCreate(BaseModel):
    """评论创建模型"""
    content: str = Field(..., min_length=1, max_length=500)


class CommentResponse(BaseModel):
    """评论响应模型"""
    id: int
    postId: int
    content: str
    author: UserResponse
    likes: int = 0
    isLiked: bool = False
    createdAt: datetime
    
    class Config:
        from_attributes = True
