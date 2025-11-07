"""
ISpeak标签相关的Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class IspeakTagBase(BaseModel):
    """ISpeak标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    bgColor: str = Field("#DB2828", description="背景颜色")
    orderNo: int = Field(0, description="排序序号")
    description: Optional[str] = Field("", description="标签描述")


class IspeakTagCreate(IspeakTagBase):
    """创建ISpeak标签"""
    pass


class IspeakTagUpdate(BaseModel):
    """更新ISpeak标签"""
    id: str = Field(..., alias="_id", description="标签ID")
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    bgColor: Optional[str] = None
    orderNo: Optional[int] = None
    description: Optional[str] = None
    
    class Config:
        populate_by_name = True


class IspeakTagInDB(IspeakTagBase):
    """数据库中的ISpeak标签模型"""
    id: str = Field(..., alias="_id")
    user: str = Field(..., description="创建用户ID")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class IspeakTagResponse(IspeakTagInDB):
    """ISpeak标签响应模型"""
    pass

