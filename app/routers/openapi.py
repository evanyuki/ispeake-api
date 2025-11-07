"""
开放API路由
"""
from fastapi import APIRouter, Query, Body, HTTPException, status
from typing import Optional

from app.schemas.response import SuccessResponse
from app.schemas.openapi import NoticeParams, GitHubDispatchParams, VersionResponse
from app.services.openapi_service import (
    NoticeService, GitHubService, QQService, HTTPProxyService
)

# 版本信息
version_router = APIRouter(prefix="/openapi", tags=["版本"])


@version_router.get("/version", response_model=SuccessResponse)
async def get_version():
    """
    获取API版本信息
    """
    version_data = VersionResponse(
        version="0.0.1",
        date="2022-06-18"
    )
    return SuccessResponse.create(data=version_data)


# 通知
notice_router = APIRouter(prefix="/open/notice", tags=["通知"])


@notice_router.get("/", response_model=SuccessResponse)
async def send_notice_get(
    type: str = Query(..., description="通知类型"),
    token: str = Query(..., description="平台token"),
    content: str = Query(..., description="消息内容"),
    title: Optional[str] = Query(None, description="消息标题")
):
    """
    发送通知（GET方式）
    """
    result = await NoticeService.send_notice(type, token, content, title)
    return SuccessResponse.create(data=result)


@notice_router.post("/", response_model=SuccessResponse)
async def send_notice_post(
    notice_params: NoticeParams = Body(...)
):
    """
    发送通知（POST方式）
    """
    result = await NoticeService.send_notice(
        notice_params.type.value,
        notice_params.token,
        notice_params.content,
        notice_params.title
    )
    return SuccessResponse.create(data=result)


# QQ
qq_router = APIRouter(prefix="/open/qq", tags=["QQ"])


@qq_router.get("/avatar")
async def get_qq_avatar(
    qq: str = Query(..., description="QQ号"),
    r: Optional[str] = Query(None, description="是否通过代理返回")
):
    """
    获取QQ头像
    不带r参数：302重定向到头像URL
    带r参数：代理返回图片内容
    """
    return await QQService.get_avatar(qq, return_proxy=bool(r))


# GitHub
github_router = APIRouter(prefix="/open/github", tags=["GitHub"])


@github_router.post("/dispatch", response_model=SuccessResponse)
async def github_dispatch_post(
    dispatch_params: GitHubDispatchParams = Body(...)
):
    """
    触发GitHub Dispatch（POST方式）
    """
    result = await GitHubService.dispatch(
        dispatch_params.token,
        dispatch_params.owner,
        dispatch_params.repo,
        dispatch_params.text
    )
    
    if result.get("success"):
        return SuccessResponse.create(
            data=result.get("headers"),
            message=result.get("message")
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message"))


@github_router.get("/dispatch", response_model=SuccessResponse)
async def github_dispatch_get(
    token: str = Query(..., description="GitHub Personal Access Token"),
    owner: str = Query(..., description="仓库所有者"),
    repo: str = Query(..., description="仓库名称"),
    text: Optional[str] = Query("kkapi dispatch", description="事件类型")
):
    """
    触发GitHub Dispatch（GET方式）
    """
    result = await GitHubService.dispatch(token, owner, repo, text)
    
    if result.get("success"):
        return SuccessResponse.create(
            data=result.get("headers"),
            message=result.get("message")
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message"))


# HTTP代理
http_router = APIRouter(prefix="/open/http", tags=["HTTP代理"])


# 注意：CORS代理功能默认禁用，需要时可以取消注释
# @http_router.get("/cors")
# async def cors_proxy(
#     url: str = Query(..., description="需要代理的URL")
# ):
#     """
#     HTTP CORS代理
#     警告：此功能可能被滥用，建议在生产环境中禁用或添加白名单
#     """
#     return await HTTPProxyService.cors_proxy(url)


# 合并所有开放API路由
router = APIRouter()
router.include_router(version_router)
router.include_router(notice_router)
router.include_router(qq_router)
router.include_router(github_router)
router.include_router(http_router)

