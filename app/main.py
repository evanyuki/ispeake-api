"""
FastAPI主入口文件
适配Vercel Serverless部署
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database import close_mongo_connection, connect_to_mongo
from app.routers import user, token, ispeak, ispeak_tag, post, openapi


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await connect_to_mongo()
    yield
    # 关闭时
    await close_mongo_connection()


app = FastAPI(
    title="KKAPI",
    description="KKAPI服务 - FastAPI版本",
    version="0.0.1",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user.router, prefix="/api")
app.include_router(token.router, prefix="/api")
app.include_router(ispeak.router, prefix="/api")
app.include_router(ispeak_tag.router, prefix="/api")
app.include_router(post.router, prefix="/api")
app.include_router(openapi.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "KKAPI - FastAPI版本", "version": "0.0.1"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Vercel需要这个handler
handler = app

