"""
帖子相关Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class CommentInPost(BaseModel):
    """帖子中的评论"""
    id: int
    postId: int
    content: str
    author: UserResponse
    likes: int = 0
    isLiked: bool = False
    createdAt: datetime
    
    class Config:
        from_attributes = True


class PostBase(BaseModel):
    """帖子基础模型"""
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=5000)
    images: Optional[list[str]] = Field(default=[], max_length=9)


class PostCreate(PostBase):
    """帖子创建模型"""
    pass


class PostUpdate(BaseModel):
    """帖子更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    images: Optional[list[str]] = Field(default=None, max_length=9)


class PostResponse(BaseModel):
    """帖子响应模型"""
    id: int
    title: str
    content: str
    images: list[str] = []
    author: UserResponse
    likes: int = 0
    commentCount: int = 0
    viewCount: int = 0
    isLiked: bool = False
    createdAt: datetime
    updatedAt: datetime
    comments: list[CommentInPost] = []
    
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """帖子列表响应"""
    id: int
    title: str
    content: str
    images: list[str] = []
    author: UserResponse
    likes: int = 0
    commentCount: int = 0
    viewCount: int = 0
    isLiked: bool = False
    createdAt: datetime
    updatedAt: datetime
    comments: list = []
    
    class Config:
        from_attributes = True


class PostFavoriteResponse(PostListResponse):
    """收藏帖子响应"""
    favoriteAt: Optional[datetime] = None
