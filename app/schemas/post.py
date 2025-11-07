"""
Post朋友圈相关的Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PostBase(BaseModel):
    """Post基础模型"""
    title: str = Field(..., min_length=1, description="文章标题")
    link: str = Field(..., min_length=1, description="文章链接")
    author: str = Field(..., description="作者名称")
    avatar: str = Field(..., description="作者头像")
    rule: Optional[str] = Field("", description="爬虫规则")
    updated: Optional[datetime] = Field(None, description="文章更新时间")
    created: Optional[datetime] = Field(None, description="文章创建时间")


class PostCreate(PostBase):
    """创建Post"""
    pass


class PostInDB(PostBase):
    """数据库中的Post模型"""
    id: str = Field(..., alias="_id")
    createdAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class PostResponse(PostInDB):
    """Post响应模型"""
    pass

