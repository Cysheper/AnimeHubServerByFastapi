"""
评论相关路由
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment, CommentLike
from app.schemas.comment import CommentCreate
from app.schemas.common import success_response

router = APIRouter(tags=["评论"])


@router.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """创建评论"""
    # 检查帖子是否存在
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    
    # 创建评论
    new_comment = Comment(
        content=comment_data.content,
        author_id=current_user.id,
        post_id=post_id
    )
    
    db.add(new_comment)
    await db.flush()
    await db.refresh(new_comment)
    
    return success_response(
        data={
            "id": new_comment.id,
            "postId": post_id,
            "content": new_comment.content,
            "author": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "avatar": current_user.get_avatar_url(),
                "createdAt": current_user.created_at.isoformat()
            },
            "likes": 0,
            "isLiked": False,
            "createdAt": new_comment.created_at.isoformat()
        },
        message="评论成功"
    )


@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """点赞/取消点赞评论"""
    # 检查评论是否存在
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查是否已点赞
    result = await db.execute(
        select(CommentLike).where(
            CommentLike.comment_id == comment_id,
            CommentLike.user_id == current_user.id
        )
    )
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        # 取消点赞
        await db.delete(existing_like)
        message = "取消点赞成功"
    else:
        # 点赞
        new_like = CommentLike(comment_id=comment_id, user_id=current_user.id)
        db.add(new_like)
        message = "点赞成功"
    
    return success_response(message=message)
