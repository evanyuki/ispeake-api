"""
Token管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path

from app.core.dependencies import get_current_user, get_db
from app.schemas.response import SuccessResponse
from app.schemas.token import TokenCreate, TokenUpdate, TokenResponse
from app.services.token_service import TokenService

router = APIRouter(prefix="/user/token", tags=["Token管理"])


@router.get("/", response_model=SuccessResponse)
async def get_token_list(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取当前用户的Token列表
    需要JWT认证
    """
    tokens = await TokenService.get_all(db, current_user["userId"])
    return SuccessResponse.create(data=tokens)


@router.post("/add", response_model=SuccessResponse)
async def add_token(
    token_data: TokenCreate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    添加Token
    需要JWT认证
    """
    try:
        token = await TokenService.add_one(
            db,
            current_user["userId"],
            token_data.title,
            token_data.value
        )
        return SuccessResponse.create(data=token, message="添加成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/update", response_model=SuccessResponse)
async def update_token(
    token_data: TokenUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新Token
    需要JWT认证
    """
    # 提取要更新的字段
    update_dict = token_data.model_dump(exclude_unset=True, exclude={"id"})
    
    if not update_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供任何更新字段")
    
    # 获取token_id (支持_id和id两种字段名)
    token_id = token_data.id if hasattr(token_data, 'id') else getattr(token_data, '_id', None)
    
    if not token_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少Token ID")
    
    result = await TokenService.update_one(
        db,
        token_id,
        current_user["userId"],
        update_dict
    )
    
    if result["matchedCount"] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token不存在或无权限修改")
    elif result["modifiedCount"] == 0:
        return SuccessResponse.create(data=result, message="没有修改任何内容")
    else:
        return SuccessResponse.create(data=result, message="更新成功")


@router.delete("/delete/{id}", response_model=SuccessResponse)
async def delete_token(
    id: str = Path(..., description="Token ID"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    删除Token
    需要JWT认证
    """
    result = await TokenService.delete_one(db, id, current_user["userId"])
    
    if result["deletedCount"] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token不存在或无权限删除")
    else:
        return SuccessResponse.create(data=result, message="删除成功")

