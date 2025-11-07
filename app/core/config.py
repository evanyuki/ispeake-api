"""
应用配置
支持从环境变量读取
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "KKAPI"
    VERSION: str = "0.0.1"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_NAME: str = "kkapi"
    DATABASE_USER: Optional[str] = None
    DATABASE_PASSWORD: Optional[str] = None
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30天
    
    # MongoDB连接池配置（Serverless优化）
    MONGO_MAX_POOL_SIZE: int = 10
    MONGO_MIN_POOL_SIZE: int = 1
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 5000
    
    # GitHub OAuth配置（可选）
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

