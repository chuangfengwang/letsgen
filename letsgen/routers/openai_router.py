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

router = APIRouter(prefix="/api/openai/v1", tags=["openai"])


class RequestContext(BaseModel):
    # 身份信息
    identity: auth.Identity
    # 各节点时间戳
    request_in_at: datetime
    # error 信息
    error: str | None = None


# @router.post("/chat/completions")
# @processor_concurrency.monitor_concurrency(metric_name="/chat/completions")  # 使用不同指标名
# async def chat_completions(
#     # request: Request,
#     # background_tasks: BackgroundTasks,
#     identity: auth.Identity = Depends(auth.any_authorize_check),
# ):
#     """
#     OpenAI Chat Completions API
#     """
#     await asyncio.sleep(0.1)
#     return {
#         "identity": identity
#     }


@router.get("/chat/completion")
async def chat_completions(account: str, model: str, duration: float = 1):
    """模拟耗时任务"""
    await asyncio.sleep(duration)
    return {"ok": True, "account": account, "model": model, "duration": duration}
