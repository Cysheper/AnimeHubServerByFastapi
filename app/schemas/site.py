"""
站点相关Schema
"""
from typing import Optional
from pydantic import BaseModel


class SiteStats(BaseModel):
    """站点统计"""
    totalPosts: int
    todayPosts: int
    totalUsers: int
    onlineUsers: int


class Fortune(BaseModel):
    """运势响应"""
    id: int
    title: str
    content: str
    type: str  # great, good, normal, bad
    icon: str


class Developer(BaseModel):
    """开发者信息"""
    id: int
    name: str
    role: str
    avatar: Optional[str] = None
    github: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class AdminStats(BaseModel):
    """管理员统计"""
    totalPosts: int
    totalComments: int
    totalUsers: int
    activeUsers: int
    todayPosts: int
    todayComments: int


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    postIds: Optional[list[int]] = None
    commentIds: Optional[list[int]] = None


class BatchDeleteResponse(BaseModel):
    """批量删除响应"""
    deletedCount: int
