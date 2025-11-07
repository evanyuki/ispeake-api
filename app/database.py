"""
MongoDB数据库连接
优化Serverless环境的连接复用
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from app.core.config import settings

# 全局连接对象
_client: Optional[AsyncIOMotorClient] = None
_db = None


async def connect_to_mongo():
    """连接到MongoDB"""
    global _client, _db
    
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.DATABASE_URL,
            maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
            minPoolSize=settings.MONGO_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        )
        _db = _client[settings.DATABASE_NAME]
        print(f"✅ 已连接到MongoDB: {settings.DATABASE_NAME}")


async def close_mongo_connection():
    """关闭MongoDB连接"""
    global _client
    if _client:
        _client.close()
        print("❌ MongoDB连接已关闭")


def get_database():
    """
    获取数据库实例
    用于依赖注入
    """
    if _db is None:
        raise Exception("数据库未初始化，请先调用 connect_to_mongo()")
    return _db


# 集合名称常量
class Collections:
    """MongoDB集合名称"""
    USERS = "kkapi_user_list"
    TOKENS = "kkapi_token_list"
    ISPEAK = "kkapi_ispeak_list"
    ISPEAK_TAGS = "kkapi_ispeak_tag_list"
    POSTS = "Post"

