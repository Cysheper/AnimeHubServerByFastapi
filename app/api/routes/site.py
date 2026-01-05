"""
站点相关路由
"""
from typing import Annotated, Optional
from datetime import datetime, date
import random
import hashlib

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_optional
from app.core.timezone import now_beijing, BEIJING_TZ
from app.models.user import User
from app.models.post import Post
from app.models.site import Fortune, Developer, UserFortune
from app.schemas.common import success_response

router = APIRouter(prefix="/site", tags=["站点"])


# 默认运势数据
DEFAULT_FORTUNES = [
    {"title": "大吉", "content": "今天是个好日子,适合追番和交友!", "type": "great", "icon": "🎉"},
    {"title": "中吉", "content": "今天运气不错,可能会遇到志同道合的朋友!", "type": "good", "icon": "✨"},
    {"title": "小吉", "content": "平稳的一天,适合安静地看动漫。", "type": "good", "icon": "🌟"},
    {"title": "吉", "content": "今天适合发帖分享你的心情!", "type": "good", "icon": "😊"},
    {"title": "末吉", "content": "虽然普通,但小确幸会出现。", "type": "normal", "icon": "🍀"},
    {"title": "凶", "content": "今天小心剧透!建议减少社交。", "type": "bad", "icon": "⚠️"},
]

# 默认开发者信息
DEFAULT_DEVELOPERS = [
    {
        "id": 1,
        "name": "主开发者",
        "role": "全栈工程师",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=developer1",
        "github": "https://github.com/developer1",
        "email": "dev@animehub.com",
        "description": "负责项目架构和核心功能开发"
    },
    {
        "id": 2,
        "name": "UI设计师",
        "role": "视觉设计师",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=designer",
        "email": "designer@animehub.com",
        "description": "负责界面设计和用户体验"
    }
]


@router.get("/stats")
async def get_site_stats(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """获取站点统计"""
    # 总帖子数
    total_posts_result = await db.execute(select(func.count(Post.id)))
    total_posts = total_posts_result.scalar() or 0
    
    # 今日新帖
    today = now_beijing().date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=BEIJING_TZ)
    today_posts_result = await db.execute(
        select(func.count(Post.id)).where(Post.created_at >= today_start)
    )
    today_posts = today_posts_result.scalar() or 0
    
    # 注册用户数
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # 在线用户数（模拟）
    online_users = random.randint(50, 200)
    
    return success_response(
        data={
            "totalPosts": total_posts,
            "todayPosts": today_posts,
            "totalUsers": total_users,
            "onlineUsers": online_users
        }
    )


@router.get("/fortune")
async def get_fortune(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)]
):
    """获取今日运势"""
    today_str = date.today().isoformat()
    
    # 使用用户ID（如果有）和日期生成固定的随机种子
    if current_user:
        seed_str = f"{current_user.id}_{today_str}"
    else:
        seed_str = f"guest_{today_str}"
    
    # 使用MD5生成确定性的索引
    hash_value = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    fortune_index = hash_value % len(DEFAULT_FORTUNES)
    
    fortune = DEFAULT_FORTUNES[fortune_index]
    
    return success_response(
        data={
            "id": fortune_index + 1,
            "title": fortune["title"],
            "content": fortune["content"],
            "type": fortune["type"],
            "icon": fortune["icon"]
        }
    )


@router.get("/developers")
async def get_developers():
    """获取开发者信息"""
    return success_response(data=DEFAULT_DEVELOPERS)
