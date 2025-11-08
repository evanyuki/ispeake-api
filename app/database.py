"""
MongoDB数据库连接
优化Serverless环境的连接复用
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import asyncio

from app.core.config import settings

# 全局连接对象
_client: Optional[AsyncIOMotorClient] = None
_db = None
_initializing = False


async def ensure_connection():
    """
    确保数据库连接可用
    使用锁机制防止并发初始化
    """
    global _client, _db, _initializing
    
    # 如果已经有连接，直接返回
    if _client is not None and _db is not None:
        return _db
    
    # 防止并发初始化
    if _initializing:
        # 等待其他协程完成初始化
        max_wait = 30  # 最多等待30秒
        waited = 0
        while _initializing and waited < max_wait:
            await asyncio.sleep(0.1)
            waited += 0.1
        
        if _db is not None:
            return _db
    
    try:
        _initializing = True
        
        # 创建新连接
        _client = AsyncIOMotorClient(
            settings.DATABASE_URL,
            maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
            minPoolSize=settings.MONGO_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            # Serverless优化配置
            connectTimeoutMS=10000,  # 连接超时
            socketTimeoutMS=10000,   # socket超时
            retryWrites=True,        # 自动重试写操作
        )
        _db = _client[settings.DATABASE_NAME]
        
        # 测试连接（使用较短的超时）
        await asyncio.wait_for(
            _client.admin.command('ping'),
            timeout=5.0
        )
        print(f"✅ MongoDB连接成功: {settings.DATABASE_NAME}")
        
    except asyncio.TimeoutError:
        print(f"❌ MongoDB连接超时")
        _client = None
        _db = None
        raise Exception("数据库连接超时")
    except Exception as e:
        print(f"❌ MongoDB连接失败: {type(e).__name__}: {e}")
        _client = None
        _db = None
        raise
    finally:
        _initializing = False
    
    return _db


async def get_db_async():
    """
    获取数据库实例（异步方法，推荐用于依赖注入）
    支持惰性初始化和连接健康检查，适配Serverless环境
    """
    global _db
    
    try:
        # 确保连接可用
        _db = await ensure_connection()
        return _db
    except Exception as e:
        print(f"❌ 获取数据库连接失败: {type(e).__name__}: {e}")
        # 重置连接状态，下次请求时重新初始化
        global _client
        _client = None
        _db = None
        raise


async def connect_to_mongo():
    """
    显式连接到MongoDB（兼容旧代码）
    在Serverless环境中，建议使用 get_db_async() 的惰性初始化
    """
    return await ensure_connection()


async def close_mongo_connection():
    """
    关闭MongoDB连接
    注意：在Serverless环境中，通常不需要主动关闭连接
    连接池会自动管理连接生命周期
    """
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("⚠️  MongoDB连接已关闭（不推荐在Serverless环境中使用）")


def get_database():
    """
    获取数据库实例（同步方法）
    ⚠️ 已弃用：在Serverless环境中，请使用 get_db_async()
    """
    global _db, _client
    
    if _db is None:
        # 快速初始化（不进行连接测试）
        if _client is None:
            _client = AsyncIOMotorClient(
                settings.DATABASE_URL,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
            )
            _db = _client[settings.DATABASE_NAME]
            print(f"⚠️  数据库同步初始化: {settings.DATABASE_NAME}")
    
    return _db


# 集合名称常量
class Collections:
    """MongoDB集合名称"""
    USERS = "kkapi_user_list"
    TOKENS = "kkapi_token_list"
    ISPEAK = "kkapi_ispeak_list"
    ISPEAK_TAGS = "kkapi_ispeak_tag_list"
    POSTS = "Post"

