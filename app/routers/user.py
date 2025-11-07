"""
用户路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import Optional

from app.core.dependencies import get_current_user, get_db
from app.core.security import hash_password, verify_password
from app.core.config import settings
from app.schemas.response import SuccessResponse
from app.schemas.user import (
    UserLogin, UserLoginResponse, UserInfoResponse,
    UserUpdate, UserChangePassword
)
from app.services.user_service import UserService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.get("/", response_model=SuccessResponse)
async def get_user_list(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取用户列表
    需要JWT认证
    """
    users = await UserService.find_all(db)
    return SuccessResponse.create(data=users)


@router.get("/id", response_model=SuccessResponse)
async def get_user_id(
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户ID
    需要JWT认证
    """
    return SuccessResponse.create(
        data={"id": current_user["userId"]},
        message="请求成功"
    )


@router.get("/init", response_model=SuccessResponse)
async def init_user(
    userName: Optional[str] = Query("admin"),
    db = Depends(get_db)
):
    """
    初始化用户（无需认证）
    只有系统中不存在用户时才能执行
    """
    # 检查是否已存在用户
    user_count = await UserService.count_users(db)
    if user_count > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="存在用户，初始化失败")
    
    # 创建初始用户
    user = await UserService.create_one(db, userName)
    return SuccessResponse.create(data=user)


@router.post("/login", response_model=SuccessResponse[UserLoginResponse])
async def login(
    credentials: UserLogin = Body(...),
    db = Depends(get_db)
):
    """
    用户登录（无需认证）
    返回JWT Token
    """
    try:
        print(f"📝 收到登录请求: username={credentials.username}")
        
        # 验证数据库连接
        if db is None:
            print("❌ 数据库未初始化")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库服务不可用"
            )
        
        # 验证用户凭证
        user = await AuthService.validate_user(db, credentials.username, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 创建Token
        token = AuthService.create_token(user)
        
        print(f"✅ 用户登录成功: {credentials.username}")
        
        return SuccessResponse.create(
            data=UserLoginResponse(
                token=token,
                userId=str(user["_id"]),
                userName=user["userName"]
            ),
            message="登录成功"
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 捕获所有其他异常
        print(f"❌ 登录处理异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录处理失败: {str(e)}"
        )


@router.get("/getUserInfo", response_model=SuccessResponse)
async def get_user_info(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    获取当前用户信息
    需要JWT认证
    """
    user = await UserService.find_by_id(db, current_user["userId"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 添加token到响应中
    user["token"] = f"Bearer {current_user.get('token', '')}"
    
    return SuccessResponse.create(data=user)


@router.patch("/update", response_model=SuccessResponse)
async def update_user_info(
    user_data: UserUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    更新用户信息
    需要JWT认证
    """
    # 只更新提供的字段
    update_dict = user_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供任何更新字段")
    
    result = await UserService.update_one(
        db, 
        current_user["userId"], 
        update_dict
    )
    
    if result["matchedCount"] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有找到对应用户")
    elif result["modifiedCount"] == 0:
        return SuccessResponse.create(data=result, message="没有修改任何内容")
    else:
        return SuccessResponse.create(data=result, message="更新成功")


@router.patch("/password", response_model=SuccessResponse)
async def change_password(
    password_data: UserChangePassword = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    修改密码
    需要JWT认证
    """
    # 验证两次密码是否一致
    if password_data.password != password_data.rpassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="两次密码不一致")
    
    # 获取用户信息（包含密码）
    user = await UserService.find_by_id(db, current_user["userId"], include_password=True)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    # 验证旧密码
    if not verify_password(password_data.oldPassword, user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")
    
    # 加密新密码并更新
    hashed_password = hash_password(password_data.password)
    result = await UserService.update_password(db, current_user["userId"], hashed_password)
    
    if result["modifiedCount"] == 1:
        return SuccessResponse.create(data="修改成功")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改失败")


@router.get("/oauth/github", response_model=SuccessResponse)
async def github_oauth(
    code: str = Query(..., description="GitHub OAuth回调code"),
    db = Depends(get_db)
):
    """
    GitHub OAuth登录（无需认证）
    """
    # 从配置中获取GitHub OAuth配置
    github_client_id = getattr(settings, 'GITHUB_CLIENT_ID', '')
    github_client_secret = getattr(settings, 'GITHUB_CLIENT_SECRET', '')
    
    if not github_client_id or not github_client_secret:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="GitHub OAuth未配置")
    
    # 执行OAuth登录
    result = await AuthService.github_oauth_login(
        db, 
        code, 
        github_client_id, 
        github_client_secret
    )
    
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="GitHub登录失败")
    
    return SuccessResponse.create(data=result)

