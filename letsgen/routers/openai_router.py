# -*- coding: utf-8 -*-
"""
# @File    : openai_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi import Cookie, Header
from pydantic import BaseModel
import asyncio

import letsgen.dependencies.auth as auth
import letsgen.monitors.concurrency_controller as concurrency_controller

router = APIRouter(prefix="/api/openai/v1", tags=["openai"])


class RequestContext(BaseModel):
    # 身份信息
    identity: auth.Identity
    # 各节点时间戳
    request_in_at: datetime
    # error 信息
    error: str | None = None


@router.post("/chat/completions")
@concurrency_controller.monitor_concurrency(metric_name="/chat/completions")  # 使用不同指标名
async def chat_completions(
    # request: Request,
    # background_tasks: BackgroundTasks,
    identity: auth.Identity = Depends(auth.any_authorize_check),
):
    """
    OpenAI Chat Completions API
    """
    await asyncio.sleep(5.)
    return {
        "identity": identity
    }


@router.get("/concurrency_metrics")
async def get_all_concurrency_metrics():
    """
    获取所有已注册的并发指标及它们当前的并发数。
    """
    all_metrics = await concurrency_controller.global_monitor_registry.get_all_concurrency_metrics()
    return {"concurrency_metrics": all_metrics}
