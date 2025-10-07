# -*- coding: utf-8 -*-
"""
# @File    : healthcheck_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:56
"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse

router = APIRouter()


@router.get("/", response_class=RedirectResponse)
@router.head("/", response_class=RedirectResponse)
@router.get("/ui", response_class=RedirectResponse)
@router.head("/ui", response_class=RedirectResponse)
@router.get("/ui/", response_class=RedirectResponse)
@router.head("/ui/", response_class=RedirectResponse)
async def to_default_home():
    """这些路径默认重定向到 UI 首页"""
    return "/ui/index.html"


@router.get("/status", response_class=PlainTextResponse)
@router.head("/status", response_class=PlainTextResponse)
async def root_check():
    """服务启动判断接口"""
    return "app is running"


@router.get("/healthcheck", response_class=PlainTextResponse)
@router.head("/healthcheck", response_class=PlainTextResponse)
async def healthcheck():
    """健康检查接口"""
    if os.path.exists('healthcheck.html'):
        return "ok"
    else:
        raise HTTPException(status_code=404, detail="service is not ready")
