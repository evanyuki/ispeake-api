"""
ISpeak标签路由
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException, status
from typing import Optional

from app.core.dependencies import get_current_user, get_current_user_optional, get_db
from app.schemas.response import SuccessResponse
from app.schemas.ispeak_tag import IspeakTagCreate, IspeakTagUpdate
from app.services.ispeak_tag_service import IspeakTagService

router = APIRouter(prefix="/ispeak/tag", tags=["ISpeak标签"])


@router.get("/", response_model=SuccessResponse)
async def get_tags(
    userId: Optional[str] = Query(None, description="用户ID"),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db = Depends(get_db)
):
    """
    获取所有标签
    可选认证：如果登录，默认获取当前用户的标签；否则需要提供userId
    """
    # 确定要查询的用户ID
    user_id = userId
    if not user_id and current_user:
        user_id = current_user["userId"]
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请提供用户ID或登录后访问")
    
    tags = await IspeakTagService.get_list(db, user_id)
    return SuccessResponse.create(data=tags)


@router.get("/list", response_model=SuccessResponse)
async def get_tag_list(
    userId: str = Query(..., description="用户ID"),
    db = Depends(get_db)
):
    """
    按用户ID获取标签列表（公开接口）
    """
    tags = await IspeakTagService.get_list(db, userId)
    return SuccessResponse.create(data=tags)


@router.get("/getByPage", response_model=SuccessResponse)
async def get_tags_by_page(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    分页获取标签
    需要JWT认证
    """
    result = await IspeakTagService.get_by_page(
        db,
        current_user["userId"],
        page,
        pageSize
    )
    return SuccessResponse.create(data=result)


@router.post("/add", response_model=SuccessResponse)
async def add_tag(
    tag_data: IspeakTagCreate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    添加标签
    需要JWT认证
    """
    try:
        tag = await IspeakTagService.add_one(
            db,
            current_user["userId"],
            tag_data.name,
            tag_data.bgColor,
            tag_data.orderNo,
            tag_data.description or ""
        )
        return SuccessResponse.create(data=tag, message="添加成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/update", response_model=SuccessResponse)
async def update_tag(
    tag_data: IspeakTagUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新标签
    需要JWT认证
    """
    try:
        # 提取要更新的字段
        update_dict = tag_data.model_dump(exclude_unset=True, exclude={"id"})
        
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供任何更新字段")
        
        tag_id = tag_data.id
        
        result = await IspeakTagService.update_one(
            db,
            tag_id,
            current_user["userId"],
            update_dict
        )
        
        if result["matchedCount"] == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在或无权限修改")
        elif result["modifiedCount"] == 0:
            return SuccessResponse.create(data=result, message="没有修改任何内容")
        else:
            return SuccessResponse.create(data=result, message="更新成功")
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

