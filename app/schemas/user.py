"""
用户相关的Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    userName: str = Field(..., min_length=1, max_length=50)
    nickName: Optional[str] = ""
    avatar: Optional[str] = ""
    desc: Optional[str] = ""
    link: Optional[str] = ""
    email: Optional[EmailStr] = ""
    homePath: Optional[str] = "/about/index"
    status: Optional[str] = "0"
    githubId: Optional[str] = ""


class UserCreate(BaseModel):
    """创建用户"""
    userName: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """更新用户信息"""
    avatar: Optional[str] = None
    desc: Optional[str] = None
    email: Optional[EmailStr] = None
    homePath: Optional[str] = None
    link: Optional[str] = None
    nickName: Optional[str] = None
    userName: Optional[str] = None
    githubId: Optional[str] = None


class UserChangePassword(BaseModel):
    """修改密码"""
    oldPassword: str = Field(..., min_length=6)
    password: str = Field(..., min_length=6)
    rpassword: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserLoginResponse(BaseModel):
    """登录响应"""
    token: str
    userId: str
    userName: str


class UserInfoResponse(UserBase):
    """用户信息响应"""
    id: str = Field(..., alias="_id")
    token: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: str = Field(..., alias="_id")
    password: str
    speakToken: Optional[str] = ""
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

