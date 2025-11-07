"""
统一响应模型
"""
from typing import Any, Literal, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """基础响应模型"""
    code: int
    message: str
    type: Literal["success", "error", "warning"]
    data: T


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应"""
    code: int = Field(0, description="响应码，0表示成功")
    message: str = Field("请求成功", description="响应消息")
    type: Literal["success"] = "success"
    data: T = Field(..., description="响应数据")
    
    @classmethod
    def create(cls, data: T, message: str = "请求成功"):
        """快速创建成功响应"""
        return cls(data=data, message=message)


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int = Field(-1, description="错误码")
    message: str = Field(..., description="错误消息")
    type: Literal["error"] = "error"
    data: Any = None
    
    @classmethod
    def create(cls, message: str, code: int = -1, data: Any = None):
        """快速创建错误响应"""
        return cls(code=code, message=message, data=data)


class PaginationResponse(BaseModel, Generic[T]):
    """分页响应"""
    total: int = Field(..., description="总数")
    items: list[T] = Field(..., description="数据列表")
    
    @classmethod
    def create(cls, total: int, items: list[T]):
        return cls(total=total, items=items)

