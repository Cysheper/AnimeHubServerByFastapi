"""
认证相关路由
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, AuthResponse
from app.schemas.common import success_response

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """用户注册"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data.username}"
    )
    
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    
    return success_response(
        data={
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "avatar": new_user.get_avatar_url(),
                "isAdmin": new_user.is_admin,
                "createdAt": new_user.created_at.isoformat()
            }
        },
        message="注册成功"
    )


@router.post("/login")
async def login(
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """用户登录"""
    # 查找用户
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号已被禁用"
        )
    
    # 生成token
    token = create_access_token(data={"sub": str(user.id)})
    
    return success_response(
        data={
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar": user.get_avatar_url(),
                "isAdmin": user.is_admin,
                "createdAt": user.created_at.isoformat()
            }
        },
        message="登录成功"
    )


@router.get("/user")
async def get_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """获取当前用户信息"""
    return success_response(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "avatar": current_user.get_avatar_url(),
            "isAdmin": current_user.is_admin,
            "createdAt": current_user.created_at.isoformat()
        }
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """用户登出"""
    # JWT无状态，客户端删除token即可
    return success_response(message="登出成功")
