"""
用户相关路由
"""
from typing import Annotated, Optional
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User, Follow
from app.models.post import Post, PostLike, PostFavorite
from app.schemas.user import UserProfileUpdate, PasswordChange, UserSettings, DeleteAccount
from app.schemas.common import success_response

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)]
):
    """获取用户资料"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.posts), selectinload(User.followers), selectinload(User.following))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 统计获赞数
    likes_count_query = (
        select(func.count(PostLike.id))
        .join(Post, Post.id == PostLike.post_id)
        .where(Post.author_id == user_id)
    )
    likes_result = await db.execute(likes_count_query)
    likes_count = likes_result.scalar() or 0
    
    return success_response(
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.get_avatar_url(),
            "signature": user.signature,
            "postsCount": len(user.posts),
            "likesCount": likes_count,
            "followersList": user.followers,
            "followingList": user.following,
            "createdAt": user.created_at.isoformat()
        }
    )


@router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """更新用户资料"""
    # 检查用户名是否重复
    if profile_data.username and profile_data.username != current_user.username:
        result = await db.execute(select(User).where(User.username == profile_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        current_user.username = profile_data.username
    
    # 检查邮箱是否重复
    if profile_data.email and profile_data.email != current_user.email:
        result = await db.execute(select(User).where(User.email == profile_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        current_user.email = profile_data.email
    
    if profile_data.signature is not None:
        current_user.signature = profile_data.signature
    
    await db.flush()
    await db.refresh(current_user)
    
    return success_response(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "signature": current_user.signature,
            "avatar": current_user.get_avatar_url(),
            "createdAt": current_user.created_at.isoformat()
        },
        message="资料更新成功"
    )


@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """修改密码"""
    if not verify_password(password_data.currentPassword, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    current_user.hashed_password = get_password_hash(password_data.newPassword)
    await db.flush()
    
    return success_response(message="密码修改成功")


@router.post("/avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传头像"""
    # 检查文件类型
    if avatar.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的图片格式，请上传jpg、png或gif格式"
        )
    
    # 检查文件大小
    content = await avatar.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小不能超过5MB"
        )
    
    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 生成文件名
    ext = avatar.filename.split(".")[-1] if avatar.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)
    
    # 更新用户头像URL
    avatar_url = f"/uploads/{filename}"
    current_user.avatar = avatar_url
    await db.flush()
    
    return success_response(
        data={"avatarUrl": avatar_url},
        message="头像上传成功"
    )


@router.get("/{user_id}/posts")
async def get_user_posts(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100)
):
    """获取用户发布的帖子"""
    offset = (page - 1) * pageSize
    
    # 检查用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 查询帖子
    query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .where(Post.author_id == user_id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(pageSize)
    )
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # 统计总数
    count_result = await db.execute(select(func.count(Post.id)).where(Post.author_id == user_id))
    total = count_result.scalar() or 0
    
    items = []
    for post in posts:
        is_liked = False
        if current_user:
            is_liked = any(like.user_id == current_user.id for like in post.likes)
        
        items.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "images": post.images or [],
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "avatar": post.author.get_avatar_url()
            },
            "likes": len(post.likes),
            "commentCount": len(post.comments),
            "viewCount": post.view_count,
            "isLiked": is_liked,
            "createdAt": post.created_at.isoformat(),
            "updatedAt": post.updated_at.isoformat()
        })
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )


@router.get("/favorites")
async def get_user_favorites(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100)
):
    """获取用户收藏的帖子"""
    offset = (page - 1) * pageSize
    
    # 查询收藏
    query = (
        select(PostFavorite)
        .options(
            selectinload(PostFavorite.post).selectinload(Post.author),
            selectinload(PostFavorite.post).selectinload(Post.likes),
            selectinload(PostFavorite.post).selectinload(Post.comments)
        )
        .where(PostFavorite.user_id == current_user.id)
        .order_by(PostFavorite.created_at.desc())
        .offset(offset)
        .limit(pageSize)
    )
    result = await db.execute(query)
    favorites = result.scalars().all()
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(PostFavorite.id)).where(PostFavorite.user_id == current_user.id)
    )
    total = count_result.scalar() or 0
    
    items = []
    for fav in favorites:
        post = fav.post
        is_liked = any(like.user_id == current_user.id for like in post.likes)
        
        items.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "avatar": post.author.get_avatar_url()
            },
            "likes": len(post.likes),
            "commentCount": len(post.comments),
            "viewCount": post.view_count,
            "isLiked": is_liked,
            "favoriteAt": fav.created_at.isoformat(),
            "createdAt": post.created_at.isoformat()
        })
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )


@router.get("/settings")
async def get_user_settings(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """获取用户设置"""
    return success_response(
        data={
            "emailNotifications": current_user.email_notifications,
            "messageNotifications": current_user.message_notifications,
            "publicProfile": current_user.public_profile
        }
    )


@router.put("/settings")
async def update_user_settings(
    settings_data: UserSettings,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """更新用户设置"""
    current_user.email_notifications = settings_data.emailNotifications
    current_user.message_notifications = settings_data.messageNotifications
    current_user.public_profile = settings_data.publicProfile
    
    await db.flush()
    
    return success_response(
        data={
            "emailNotifications": current_user.email_notifications,
            "messageNotifications": current_user.message_notifications,
            "publicProfile": current_user.public_profile
        },
        message="设置已更新"
    )


@router.delete("/account")
async def delete_account(
    delete_data: DeleteAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """删除账号"""
    if not verify_password(delete_data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误"
        )
    
    await db.delete(current_user)
    
    return success_response(message="账号已删除")


@router.post("/{user_id}/follow")
async def follow_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """关注/取消关注用户"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能关注自己"
        )
    
    # 检查用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查是否已关注
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id
        )
    )
    existing_follow = result.scalar_one_or_none()
    
    if existing_follow:
        # 取消关注
        await db.delete(existing_follow)
        return success_response(
            data={"isFollowing": False},
            message="已取消关注"
        )
    else:
        # 关注
        new_follow = Follow(follower_id=current_user.id, following_id=user_id)
        db.add(new_follow)
        return success_response(
            data={"isFollowing": True},
            message="关注成功"
        )


@router.get("/{user_id}/followers")
async def get_followers(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100)
):
    """获取粉丝列表"""
    offset = (page - 1) * pageSize
    
    # 检查用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 查询粉丝
    query = (
        select(Follow)
        .options(selectinload(Follow.follower))
        .where(Follow.following_id == user_id)
        .order_by(Follow.created_at.desc())
        .offset(offset)
        .limit(pageSize)
    )
    result = await db.execute(query)
    follows = result.scalars().all()
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(Follow.id)).where(Follow.following_id == user_id)
    )
    total = count_result.scalar() or 0
    
    # 检查当前用户是否关注了这些粉丝
    items = []
    for follow in follows:
        follower = follow.follower
        is_following = False
        
        if current_user:
            follow_check = await db.execute(
                select(Follow).where(
                    Follow.follower_id == current_user.id,
                    Follow.following_id == follower.id
                )
            )
            is_following = follow_check.scalar_one_or_none() is not None
        
        items.append({
            "id": follower.id,
            "username": follower.username,
            "avatar": follower.get_avatar_url(),
            "signature": follower.signature,
            "isFollowing": is_following,
            "followedAt": follow.created_at.isoformat()
        })
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )


@router.get("/{user_id}/following")
async def get_following(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100)
):
    """获取关注列表"""
    offset = (page - 1) * pageSize
    
    # 检查用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 查询关注
    query = (
        select(Follow)
        .options(selectinload(Follow.following))
        .where(Follow.follower_id == user_id)
        .order_by(Follow.created_at.desc())
        .offset(offset)
        .limit(pageSize)
    )
    result = await db.execute(query)
    follows = result.scalars().all()
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(Follow.id)).where(Follow.follower_id == user_id)
    )
    total = count_result.scalar() or 0
    
    items = []
    for follow in follows:
        following_user = follow.following
        is_following = True  # 查询的就是关注列表，所以肯定是true
        
        items.append({
            "id": following_user.id,
            "username": following_user.username,
            "avatar": following_user.get_avatar_url(),
            "signature": following_user.signature,
            "isFollowing": is_following,
            "followedAt": follow.created_at.isoformat()
        })
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )
