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

import asyncio

import letsgen.dependencies.auth as auth
from letsgen.service.openai_service import OpenAIService
from letsgen.service.llm_api_transfer import LlmTransferService

router = APIRouter(prefix="/api/openai/v1", tags=["openai"])
llmTransferService: LlmTransferService = OpenAIService()


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    background_tasks: BackgroundTasks,
    identity: auth.Identity = Depends(auth.header_authorize_check),
):
    """
    OpenAI Chat Completions API
    """
    response = await llmTransferService.run(request.state.context)
    return response


@router.get("/chat/completion")
async def get_chat_completions(account: str, model: str, duration: float = 1):
    """模拟耗时任务"""
    await asyncio.sleep(duration)
    return {"ok": True, "account": account, "model": model, "duration": duration}
