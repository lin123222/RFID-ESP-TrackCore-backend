from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

# 定义泛型类型变量
T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应模型"""
    status: str = "success"
    message: str
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    status: str = "error"
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    database: str
    app_name: str
    version: str
