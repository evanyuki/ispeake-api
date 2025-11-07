"""
朋友圈路由
"""
from fastapi import APIRouter, Depends, Body

from app.core.dependencies import get_current_user, get_db
from app.schemas.response import SuccessResponse
from app.schemas.post import PostCreate
from app.services.post_service import PostService

router = APIRouter(prefix="/post", tags=["朋友圈"])


@router.get("/", response_model=SuccessResponse)
async def get_all_posts(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取所有文章
    需要JWT认证
    """
    posts = await PostService.find_all(db)
    return SuccessResponse.create(data=posts)


@router.post("/add", response_model=SuccessResponse)
async def add_post(
    post_data: PostCreate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    添加文章
    需要JWT认证
    """
    post = await PostService.create_one(
        db,
        post_data.title,
        post_data.link,
        post_data.author,
        post_data.avatar,
        post_data.rule or "",
        post_data.updated,
        post_data.created
    )
    return SuccessResponse.create(data=post, message="添加成功")

