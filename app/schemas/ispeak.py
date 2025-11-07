"""
ISpeak相关的Pydantic模型
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class IspeakBase(BaseModel):
    """ISpeak基础模型"""
    title: Optional[str] = Field("", description="标题")
    content: str = Field(..., min_length=1, description="内容")
    type: str = Field("0", description="类型: 0=所有人 1=登录 2=自己")
    showComment: str = Field("1", description="是否可评论: 0=不可以 1=可以")


class IspeakCreate(IspeakBase):
    """创建ISpeak"""
    tag: str = Field(..., description="标签ID")


class IspeakCreateByToken(IspeakBase):
    """通过Token创建ISpeak"""
    token: str = Field(..., description="Token值")
    tag: str = Field(..., description="标签ID")


class IspeakUpdate(BaseModel):
    """更新ISpeak"""
    id: str = Field(..., alias="_id", description="ISpeak ID")
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    tag: Optional[str] = None
    showComment: Optional[str] = None
    
    class Config:
        populate_by_name = True


class IspeakStatusUpdate(BaseModel):
    """更新ISpeak评论状态"""
    id: str = Field(..., alias="_id", description="ISpeak ID")
    showComment: str = Field(..., description="是否可评论")
    
    class Config:
        populate_by_name = True


class IspeakAuthor(BaseModel):
    """作者信息"""
    nickName: str
    avatar: str


class IspeakTag(BaseModel):
    """标签信息"""
    id: str = Field(..., alias="_id")
    name: str
    bgColor: str
    
    class Config:
        populate_by_name = True


class IspeakInDB(IspeakBase):
    """数据库中的ISpeak模型"""
    id: str = Field(..., alias="_id")
    author: str = Field(..., description="作者ID")
    tag: str = Field(..., description="标签ID")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class IspeakPublicResponse(BaseModel):
    """ISpeak公开响应（处理可见性）"""
    id: str = Field(..., alias="_id")
    title: Optional[str] = ""
    content: str
    type: str
    showComment: str
    author: Optional[IspeakAuthor] = None
    tag: Optional[IspeakTag] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

