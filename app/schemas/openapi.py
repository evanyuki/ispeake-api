"""
开放API相关的Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class NoticeType(str, Enum):
    """通知类型枚举"""
    QMSG = "qmsg"
    SERVERCHAIN = "serverchain"
    PUSHPLUS = "pushplus"
    PUSHPLUSHXTRIP = "pushplushxtrip"
    DINGTALK = "dingtalk"
    WECOM = "wecom"
    BARK = "bark"
    GOCQHTTP = "gocqhttp"
    PUSHDEER = "pushdeer"
    IGOT = "igot"
    TELEGRAM = "telegram"


class NoticeParams(BaseModel):
    """通知参数（POST）"""
    type: NoticeType = Field(..., description="通知类型")
    token: str = Field(..., description="平台token")
    content: str = Field(..., description="消息内容")
    title: Optional[str] = Field(None, description="消息标题")


class GitHubDispatchParams(BaseModel):
    """GitHub Dispatch参数"""
    token: str = Field(..., description="GitHub Personal Access Token")
    owner: str = Field(..., description="仓库所有者")
    repo: str = Field(..., description="仓库名称")
    text: Optional[str] = Field("kkapi dispatch", description="事件类型")


class VersionResponse(BaseModel):
    """版本信息响应"""
    version: str
    date: str

