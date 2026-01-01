"""
用户相关Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ========== 基础模型 ==========

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=32)


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    avatar: str
    isAdmin: bool = False
    createdAt: datetime
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """用户资料响应模型"""
    signature: Optional[str] = None
    postsCount: int = 0
    likesCount: int = 0
    followersCount: int = 0
    followingCount: int = 0
    isAdmin: bool = False


class UserProfileUpdate(BaseModel):
    """用户资料更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    email: Optional[EmailStr] = None
    signature: Optional[str] = Field(None, max_length=200)


class PasswordChange(BaseModel):
    """修改密码模型"""
    currentPassword: str
    newPassword: str = Field(..., min_length=6, max_length=32)


class UserSettings(BaseModel):
    """用户设置模型"""
    emailNotifications: bool = True
    messageNotifications: bool = True
    publicProfile: bool = True


class DeleteAccount(BaseModel):
    """删除账号模型"""
    password: str


# ========== 关注相关 ==========

class FollowUserResponse(BaseModel):
    """关注用户响应"""
    id: int
    username: str
    avatar: str
    signature: Optional[str] = None
    isFollowing: bool = False
    followedAt: datetime


# ========== 认证响应 ==========

class AuthResponse(BaseModel):
    """认证响应"""
    token: str
    user: UserResponse
