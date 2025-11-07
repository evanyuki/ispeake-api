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
        try:
            _client = AsyncIOMotorClient(
                settings.DATABASE_URL,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            _db = _client[settings.DATABASE_NAME]
            
            # 测试连接
            await _client.admin.command('ping')
            print(f"✅ 已连接到MongoDB: {settings.DATABASE_NAME}")
        except Exception as e:
            print(f"❌ MongoDB连接失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise


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
    global _db
    
    if _db is None:
        print("❌ 数据库未初始化")
        raise Exception("数据库未初始化，请先调用 connect_to_mongo()")
    
    # 在 Serverless 环境中，检查连接是否仍然有效
    try:
        return _db
    except Exception as e:
        print(f"❌ 获取数据库连接失败: {type(e).__name__}: {e}")
        raise


# 集合名称常量
class Collections:
    """MongoDB集合名称"""
    USERS = "kkapi_user_list"
    TOKENS = "kkapi_token_list"
    ISPEAK = "kkapi_ispeak_list"
    ISPEAK_TAGS = "kkapi_ispeak_tag_list"
    POSTS = "Post"

