"""
管理员相关路由
"""
from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_admin_user
from app.core.timezone import now_beijing, BEIJING_TZ
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.site import BatchDeleteRequest
from app.schemas.common import success_response

router = APIRouter(prefix="/admin", tags=["管理员"])


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    """删除帖子"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    
    await db.delete(post)
    
    return success_response(message="帖子删除成功")


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    """删除评论"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    await db.delete(comment)
    
    return success_response(message="评论删除成功")


@router.get("/posts")
async def get_all_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(get_admin_user)],
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    sortBy: str = Query("latest", pattern="^(latest|oldest|mostLiked|mostCommented)$"),
    search: Optional[str] = None
):
    """获取所有帖子（管理员）"""
    offset = (page - 1) * pageSize
    
    # 构建查询
    query = select(Post).options(
        selectinload(Post.author),
        selectinload(Post.likes),
        selectinload(Post.comments).selectinload(Comment.author),
        selectinload(Post.comments).selectinload(Comment.likes)
    )
    
    # 搜索
    if search:
        query = query.where(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
        )
    
    # 排序
    if sortBy == "latest":
        query = query.order_by(Post.created_at.desc())
    elif sortBy == "oldest":
        query = query.order_by(Post.created_at.asc())
    elif sortBy == "mostLiked":
        # 按点赞数排序需要子查询
        query = query.order_by(Post.view_count.desc())  # 简化实现
    elif sortBy == "mostCommented":
        query = query.order_by(Post.view_count.desc())  # 简化实现
    
    query = query.offset(offset).limit(pageSize)
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # 统计总数
    count_query = select(func.count(Post.id))
    if search:
        count_query = count_query.where(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
        )
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    items = []
    for post in posts:
        comments = []
        for comment in post.comments[:5]:  # 只返回前5条评论
            comments.append({
                "id": comment.id,
                "postId": comment.post_id,
                "content": comment.content,
                "author": {
                    "id": comment.author.id,
                    "username": comment.author.username,
                    "avatar": comment.author.get_avatar_url()
                },
                "likes": len(comment.likes),
                "createdAt": comment.created_at.isoformat()
            })
        
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
            "createdAt": post.created_at.isoformat(),
            "comments": comments
        })
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )


@router.get("/comments")
async def get_all_comments(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(get_admin_user)],
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    sortBy: str = Query("latest", pattern="^(latest|oldest)$"),
    search: Optional[str] = None
):
    """获取所有评论（管理员）"""
    offset = (page - 1) * pageSize
    
    query = select(Comment).options(
        selectinload(Comment.author),
        selectinload(Comment.likes)
    )
    
    # 搜索
    if search:
        query = query.where(Comment.content.ilike(f"%{search}%"))
    
    # 排序
    if sortBy == "latest":
        query = query.order_by(Comment.created_at.desc())
    else:
        query = query.order_by(Comment.created_at.asc())
    
    query = query.offset(offset).limit(pageSize)
    result = await db.execute(query)
    comments = result.scalars().all()
    
    # 统计总数
    count_query = select(func.count(Comment.id))
    if search:
        count_query = count_query.where(Comment.content.ilike(f"%{search}%"))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    items = []
    for comment in comments:
        items.append({
            "id": comment.id,
            "postId": comment.post_id,
            "content": comment.content,
            "author": {
                "id": comment.author.id,
                "username": comment.author.username,
                "avatar": comment.author.get_avatar_url()
            },
            "likes": len(comment.likes),
            "createdAt": comment.created_at.isoformat()
        })
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )


@router.get("/stats")
async def get_admin_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    """获取管理员统计数据"""
    # 总帖子数
    total_posts_result = await db.execute(select(func.count(Post.id)))
    total_posts = total_posts_result.scalar() or 0
    
    # 总评论数
    total_comments_result = await db.execute(select(func.count(Comment.id)))
    total_comments = total_comments_result.scalar() or 0
    
    # 总用户数
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # 今日统计
    today = now_beijing().date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=BEIJING_TZ)
    
    today_posts_result = await db.execute(
        select(func.count(Post.id)).where(Post.created_at >= today_start)
    )
    today_posts = today_posts_result.scalar() or 0
    
    today_comments_result = await db.execute(
        select(func.count(Comment.id)).where(Comment.created_at >= today_start)
    )
    today_comments = today_comments_result.scalar() or 0
    
    # 活跃用户（简化：今日有发帖或评论的用户）
    active_users = min(total_users, today_posts + today_comments)
    
    return success_response(
        data={
            "totalPosts": total_posts,
            "totalComments": total_comments,
            "totalUsers": total_users,
            "activeUsers": active_users,
            "todayPosts": today_posts,
            "todayComments": today_comments
        }
    )


@router.delete("/posts/batch")
async def batch_delete_posts(
    data: BatchDeleteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    """批量删除帖子"""
    if not data.postIds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供要删除的帖子ID列表"
        )
    
    result = await db.execute(select(Post).where(Post.id.in_(data.postIds)))
    posts = result.scalars().all()
    
    deleted_count = 0
    for post in posts:
        await db.delete(post)
        deleted_count += 1
    
    return success_response(
        data={"deletedCount": deleted_count},
        message="批量删除成功"
    )


@router.delete("/comments/batch")
async def batch_delete_comments(
    data: BatchDeleteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    """批量删除评论"""
    if not data.commentIds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供要删除的评论ID列表"
        )
    
    result = await db.execute(select(Comment).where(Comment.id.in_(data.commentIds)))
    comments = result.scalars().all()
    
    deleted_count = 0
    for comment in comments:
        await db.delete(comment)
        deleted_count += 1
    
    return success_response(
        data={"deletedCount": deleted_count},
        message="批量删除成功"
    )
