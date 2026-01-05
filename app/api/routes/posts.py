"""
帖子相关路由
"""
from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.core.timezone import now_beijing
from app.models.user import User
from app.models.post import Post, PostLike, PostFavorite
from app.models.comment import Comment
from app.schemas.post import PostCreate, PostUpdate
from app.schemas.common import success_response

router = APIRouter(prefix="/posts", tags=["帖子"])


def format_post(post: Post, current_user: Optional[User] = None) -> dict:
    """格式化帖子响应"""
    is_liked = False
    if current_user:
        is_liked = any(like.user_id == current_user.id for like in post.likes)
    
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "images": post.images or [],
        "author": {
            "id": post.author.id,
            "username": post.author.username,
            "email": post.author.email,
            "avatar": post.author.get_avatar_url(),
            "createdAt": post.author.created_at.isoformat()
        },
        "likes": len(post.likes),
        "commentCount": len(post.comments),
        "viewCount": post.view_count,
        "isLiked": is_liked,
        "createdAt": post.created_at.isoformat(),
        "updatedAt": post.updated_at.isoformat(),
        "comments": []
    }


def format_post_detail(post: Post, current_user: Optional[User] = None) -> dict:
    """格式化帖子详情响应（包含评论）"""
    result = format_post(post, current_user)
    
    comments = []
    for comment in post.comments:
        is_comment_liked = False
        if current_user:
            is_comment_liked = any(like.user_id == current_user.id for like in comment.likes)
        
        comments.append({
            "id": comment.id,
            "postId": comment.post_id,
            "content": comment.content,
            "author": {
                "id": comment.author.id,
                "username": comment.author.username,
                "email": comment.author.email,
                "avatar": comment.author.get_avatar_url(),
                "createdAt": comment.author.created_at.isoformat()
            },
            "likes": len(comment.likes),
            "isLiked": is_comment_liked,
            "createdAt": comment.created_at.isoformat()
        })
    
    result["comments"] = comments
    return result


@router.get("")
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """获取帖子列表"""
    offset = (page - 1) * limit
    
    # 查询帖子
    query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # 查询总数
    count_query = select(func.count(Post.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    items = [format_post(post, current_user) for post in posts]
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": offset + len(items) < total
        }
    )


@router.get("/hot")
async def get_hot_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """获取热门帖子"""
    offset = (page - 1) * limit
    
    # 按点赞数+评论数排序
    query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .order_by(desc(Post.view_count))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.scalars().all()
    
    count_query = select(func.count(Post.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    items = [format_post(post, current_user) for post in posts]
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": offset + len(items) < total
        }
    )


@router.get("/search")
async def search_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """搜索帖子"""
    offset = (page - 1) * limit
    
    # 搜索标题和内容
    search_filter = Post.title.ilike(f"%{keyword}%") | Post.content.ilike(f"%{keyword}%")
    
    query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .where(search_filter)
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # 查询总数
    count_query = select(func.count(Post.id)).where(search_filter)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    items = [format_post(post, current_user) for post in posts]
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "keyword": keyword,
            "hasMore": offset + len(items) < total
        }
    )


@router.get("/recommended")
async def get_recommended_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """获取推荐帖子"""
    offset = (page - 1) * limit
    
    # 简单的推荐算法：随机排序
    query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .order_by(func.random())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.scalars().all()
    
    count_query = select(func.count(Post.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    items = [format_post(post, current_user) for post in posts]
    
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": offset + len(items) < total
        }
    )


@router.get("/{post_id}")
async def get_post_detail(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)]
):
    """获取帖子详情"""
    query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments).selectinload(Comment.author),
            selectinload(Post.comments).selectinload(Comment.likes)
        )
        .where(Post.id == post_id)
    )
    result = await db.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    
    # 增加浏览量
    post.view_count += 1
    await db.flush()
    
    return success_response(data=format_post_detail(post, current_user))


@router.post("")
async def create_post(
    post_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """创建帖子"""
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        images=post_data.images or [],
        author_id=current_user.id
    )
    
    db.add(new_post)
    await db.flush()
    await db.refresh(new_post)
    
    return success_response(
        data={
            "id": new_post.id,
            "title": new_post.title,
            "content": new_post.content,
            "images": new_post.images or [],
            "author": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "avatar": current_user.get_avatar_url(),
                "createdAt": current_user.created_at.isoformat()
            },
            "likes": 0,
            "commentCount": 0,
            "viewCount": 0,
            "isLiked": False,
            "createdAt": new_post.created_at.isoformat(),
            "updatedAt": new_post.updated_at.isoformat(),
            "comments": []
        },
        message="发布成功"
    )


@router.put("/{post_id}")
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """修改帖子"""
    # 查询帖子
    query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .where(Post.id == post_id)
    )
    result = await db.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    
    # 检查是否是作者本人
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此帖子"
        )
    
    # 更新字段
    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.images is not None:
        post.images = post_data.images
    
    post.updated_at = now_beijing()
    
    await db.flush()
    await db.refresh(post)
    
    return success_response(
        data=format_post(post, current_user),
        message="修改成功"
    )


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """删除帖子"""
    # 查询帖子
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    
    # 检查是否是作者本人或管理员
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此帖子"
        )
    
    # 删除相关的点赞记录
    await db.execute(
        select(PostLike).where(PostLike.post_id == post_id)
    )
    from sqlalchemy import delete
    await db.execute(delete(PostLike).where(PostLike.post_id == post_id))
    
    # 删除相关的收藏记录
    await db.execute(delete(PostFavorite).where(PostFavorite.post_id == post_id))
    
    # 删除相关的评论点赞和评论
    from app.models.comment import CommentLike
    comments_result = await db.execute(select(Comment.id).where(Comment.post_id == post_id))
    comment_ids = [row[0] for row in comments_result.fetchall()]
    if comment_ids:
        await db.execute(delete(CommentLike).where(CommentLike.comment_id.in_(comment_ids)))
        await db.execute(delete(Comment).where(Comment.post_id == post_id))
    
    # 删除帖子
    await db.delete(post)
    
    return success_response(message="删除成功")


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """点赞/取消点赞帖子"""
    # 检查帖子是否存在
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    
    # 检查是否已点赞
    result = await db.execute(
        select(PostLike).where(
            PostLike.post_id == post_id,
            PostLike.user_id == current_user.id
        )
    )
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        # 取消点赞
        await db.delete(existing_like)
        message = "取消点赞成功"
    else:
        # 点赞
        new_like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        message = "点赞成功"
    
    return success_response(message=message)


@router.post("/{post_id}/favorite")
async def favorite_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """收藏/取消收藏帖子"""
    # 检查帖子是否存在
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    
    # 检查是否已收藏
    result = await db.execute(
        select(PostFavorite).where(
            PostFavorite.post_id == post_id,
            PostFavorite.user_id == current_user.id
        )
    )
    existing_favorite = result.scalar_one_or_none()
    
    if existing_favorite:
        # 取消收藏
        await db.delete(existing_favorite)
        return success_response(
            data={"isFavorited": False},
            message="已取消收藏"
        )
    else:
        # 收藏
        new_favorite = PostFavorite(post_id=post_id, user_id=current_user.id)
        db.add(new_favorite)
        return success_response(
            data={"isFavorited": True},
            message="收藏成功"
        )
