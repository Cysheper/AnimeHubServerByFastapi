"""
动漫Hub API - 主入口文件
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.core.config import settings
from app.core.database import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    
    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动成功!")
    print(f"📚 API文档: http://localhost:8080/docs")
    print(f"🔧 数据库: {settings.DATABASE_URL}")
    
    yield
    
    # 关闭时的清理工作
    print("👋 服务器关闭")


# 创建应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="动漫Hub后端API服务 - 一个动漫爱好者交流平台",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )


# 挂载静态文件（用于头像上传）
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# 注册API路由
app.include_router(api_router, prefix="/api")


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": settings.APP_VERSION}


# 根路由
@app.get("/")
async def root():
    """API根路由"""
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": "/api"
    }
