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
    获取数据库实例（同步方法）
    注意：在Serverless环境中，建议使用 get_db_async() 来确保正确初始化
    """
    global _db
    
    if _db is None:
        # 尝试快速初始化（不进行连接测试）
        global _client
        if _client is None:
            _client = AsyncIOMotorClient(
                settings.DATABASE_URL,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            _db = _client[settings.DATABASE_NAME]
            print(f"⚠️  数据库惰性初始化（同步）: {settings.DATABASE_NAME}")
    
    return _db


async def get_db_async():
    """
    获取数据库实例（异步方法，推荐用于依赖注入）
    支持惰性初始化，适配Serverless环境
    """
    global _db
    
    # 如果数据库未初始化，自动初始化
    if _db is None:
        print("⚠️  数据库未初始化，正在进行惰性初始化...")
        await connect_to_mongo()
    
    return _db


# 集合名称常量
class Collections:
    """MongoDB集合名称"""
    USERS = "kkapi_user_list"
    TOKENS = "kkapi_token_list"
    ISPEAK = "kkapi_ispeak_list"
    ISPEAK_TAGS = "kkapi_ispeak_tag_list"
    POSTS = "Post"

