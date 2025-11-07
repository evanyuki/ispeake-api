"""
FastAPI依赖注入
用于替代NestJS的装饰器系统
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_token
from app.database import get_db_async

# HTTP Bearer认证
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    获取当前用户（必须登录）
    替代NestJS的JWT Guard
    
    Returns:
        {
            "userId": "ObjectId字符串",
            "userName": "用户名"
        }
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    return {
        "userId": payload.get("userId"),
        "userName": payload.get("userName")
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)
) -> Optional[dict]:
    """
    获取当前用户（可选登录）
    替代NestJS的 @IsLogin() 装饰器
    
    Returns:
        登录: {"userId": "...", "userName": "..."}
        未登录: None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        return {
            "userId": payload.get("userId"),
            "userName": payload.get("userName")
        }
    except HTTPException:
        return None


async def get_db():
    """
    获取数据库连接
    支持惰性初始化，适配Serverless环境
    """
    return await get_db_async()


# 导出常用依赖
CurrentUser = Depends(get_current_user)
CurrentUserOptional = Depends(get_current_user_optional)
Database = Depends(get_db)

