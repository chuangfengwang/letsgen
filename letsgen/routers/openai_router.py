# -*- coding: utf-8 -*-
"""
# @File    : openai_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""
from __future__ import annotations

import asyncio
from typing import cast

from fastapi import APIRouter, Request, Response, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse

import letsgen.dependencies.auth as auth
from letsgen.entity.llm_entity import LlmRequestContext
from letsgen.service.llm_api_transfer import LlmTransferService
from letsgen.service.openai_service import OpenAiService

router = APIRouter(prefix="/api/openai/v1", tags=["openai"])
llmTransferService: LlmTransferService = OpenAiService()


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    identity: auth.Identity = Depends(auth.header_authorize_check),
):
    """
    OpenAI Chat Completions API
    """
    context = cast(LlmRequestContext, request.state.context)
    provider_resp = await llmTransferService.run(context)

    if context.is_stream:
        return StreamingResponse(
            llmTransferService.stream_generator(provider_resp, request.state.context),
            media_type="text/event-stream",
            headers={
                "X-Request-Id": context.letsgen_req_id,
                "qtraceid": context.trace_id,
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        response.headers["X-Request-Id"] = context.letsgen_req_id
        response.headers["qtraceid"] = context.trace_id
        return provider_resp


@router.get("/chat/completion")
async def get_chat_completions(account: str, model: str, duration: float = 1):
    """模拟耗时任务"""
    await asyncio.sleep(duration)
    return {"ok": True, "account": account, "model": model, "duration": duration}
