"""
Token相关的Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TokenBase(BaseModel):
    """Token基础模型"""
    title: str = Field(..., min_length=1, max_length=100, description="Token标题")
    value: str = Field(..., min_length=1, description="Token值")


class TokenCreate(TokenBase):
    """创建Token"""
    pass


class TokenUpdate(BaseModel):
    """更新Token"""
    id: str = Field(..., alias="_id", description="Token ID")
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    value: Optional[str] = Field(None, min_length=1)
    
    class Config:
        populate_by_name = True


class TokenInDB(TokenBase):
    """数据库中的Token模型"""
    id: str = Field(..., alias="_id")
    user: str = Field(..., description="用户ID")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class TokenResponse(TokenInDB):
    """Token响应模型"""
    pass

