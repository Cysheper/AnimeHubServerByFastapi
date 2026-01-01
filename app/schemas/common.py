"""
通用响应模型
"""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = 200
    message: str = "Success"
    data: Optional[T] = None


class PaginatedData(BaseModel, Generic[T]):
    """分页数据模型"""
    items: list[T]
    total: int
    page: int
    limit: int
    hasMore: bool


def success_response(data: Any = None, message: str = "Success") -> dict:
    """成功响应"""
    return {"code": 200, "message": message, "data": data}


def error_response(code: int, message: str) -> dict:
    """错误响应"""
    return {"code": code, "message": message, "data": None}
