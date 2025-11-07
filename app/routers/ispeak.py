"""
ISpeak路由
"""
from fastapi import APIRouter, Depends, Query, Body, Path, HTTPException, status
from typing import Optional

from app.core.dependencies import get_current_user, get_current_user_optional, get_db
from app.schemas.response import SuccessResponse
from app.schemas.ispeak import (
    IspeakCreate, IspeakCreateByToken, IspeakUpdate, IspeakStatusUpdate
)
from app.services.ispeak_service import IspeakService
from app.services.token_service import TokenService

router = APIRouter(prefix="/ispeak", tags=["ISpeak"])


@router.get("/", response_model=SuccessResponse)
async def get_ispeak_by_page(
    author: str = Query(..., description="作者ID"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db = Depends(get_db)
):
    """
    分页获取ISpeak（公开接口，带可见性控制）
    可选认证
    """
    result = await IspeakService.get_by_page(
        db,
        author,
        page,
        pageSize,
        current_user
    )
    return SuccessResponse.create(data=result)


@router.get("/getByPage", response_model=SuccessResponse)
async def get_ispeak_by_page_admin(
    page: int = Query(..., ge=1, description="页码"),
    pageSize: int = Query(..., ge=1, le=100, description="每页数量"),
    author: Optional[str] = Query(None, description="作者ID"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    分页获取ISpeak（管理接口）
    需要JWT认证
    """
    # 如果没有提供author，使用当前用户
    author_id = author or current_user["userId"]
    
    result = await IspeakService.get_by_page_admin(
        db,
        page,
        pageSize,
        author_id
    )
    return SuccessResponse.create(data=result)


@router.post("/add", response_model=SuccessResponse)
async def add_ispeak(
    ispeak_data: IspeakCreate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    添加ISpeak
    需要JWT认证
    """
    try:
        ispeak = await IspeakService.add_one(
            db,
            current_user["userId"],
            ispeak_data.content,
            ispeak_data.tag,
            ispeak_data.title or "",
            ispeak_data.type,
            ispeak_data.showComment
        )
        return SuccessResponse.create(data=ispeak, message="添加成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/addByToken", response_model=SuccessResponse)
async def add_ispeak_by_token(
    ispeak_data: IspeakCreateByToken = Body(...),
    db = Depends(get_db)
):
    """
    通过Token添加ISpeak（无需JWT认证）
    使用Token进行身份验证
    """
    try:
        # 验证Token（title为"speak"的token）
        token_info = await TokenService.validate_token(
            db,
            "speak",
            ispeak_data.token
        )
        
        if not token_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效")
        
        # 使用Token对应的用户作为作者
        author_id = token_info["user"]
        
        ispeak = await IspeakService.add_one(
            db,
            author_id,
            ispeak_data.content,
            ispeak_data.tag,
            ispeak_data.title or "",
            ispeak_data.type,
            ispeak_data.showComment
        )
        return SuccessResponse.create(data=ispeak, message="添加成功")
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/update", response_model=SuccessResponse)
async def update_ispeak(
    ispeak_data: IspeakUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新ISpeak
    需要JWT认证，只能更新自己的ISpeak
    """
    try:
        # 提取要更新的字段
        update_dict = ispeak_data.model_dump(exclude_unset=True, exclude={"id"})
        
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供任何更新字段")
        
        ispeak_id = ispeak_data.id
        
        result = await IspeakService.update_one(
            db,
            ispeak_id,
            current_user["userId"],
            update_dict
        )
        
        if result["matchedCount"] == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ISpeak不存在或无权限修改")
        elif result["modifiedCount"] == 0:
            return SuccessResponse.create(data=result, message="没有修改任何内容")
        else:
            return SuccessResponse.create(data=result, message="更新成功")
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/status/", response_model=SuccessResponse)
async def update_ispeak_status(
    status_data: IspeakStatusUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新ISpeak评论状态
    需要JWT认证
    """
    result = await IspeakService.update_status(
        db,
        status_data.id,
        current_user["userId"],
        status_data.showComment
    )
    
    if result["matchedCount"] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ISpeak不存在或无权限修改")
    elif result["modifiedCount"] == 0:
        return SuccessResponse.create(data=result, message="没有修改任何内容")
    else:
        return SuccessResponse.create(data=result, message="更新成功")


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_ispeak(
    id: str = Path(..., description="ISpeak ID"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    删除ISpeak
    需要JWT认证，只能删除自己的ISpeak
    """
    result = await IspeakService.delete_one(db, id, current_user["userId"])
    
    if result["deletedCount"] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ISpeak不存在或无权限删除")
    else:
        return SuccessResponse.create(data=result, message="删除成功")


@router.get("/get/{id}", response_model=SuccessResponse)
async def get_ispeak_by_id(
    id: str = Path(..., description="ISpeak ID"),
    db = Depends(get_db)
):
    """
    获取单个ISpeak（无需认证）
    """
    ispeak = await IspeakService.find_by_id(db, id)
    
    if not ispeak:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ISpeak不存在")
    
    return SuccessResponse.create(data=ispeak)

