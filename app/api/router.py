"""
API路由聚合
"""
from fastapi import APIRouter

from app.api.routes import auth, posts, comments, users, site, admin

api_router = APIRouter()

# 注册所有路由
api_router.include_router(auth.router)
api_router.include_router(posts.router)
api_router.include_router(comments.router)
api_router.include_router(users.router)
api_router.include_router(site.router)
api_router.include_router(admin.router)
