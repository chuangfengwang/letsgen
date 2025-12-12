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

from fastapi import APIRouter, Request, Response, Depends, BackgroundTasks, FastAPI
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse
from starlette.middleware.cors import CORSMiddleware
from watchfiles import awatch

import letsgen.dependencies.auth as auth
from letsgen.entity.llm_entity import LlmRequestContext
from letsgen.service.llm_api_transfer import LlmTransferService
from letsgen.service.openai_service import OpenAiChatCompletionsService
from letsgen.utils.chunk_response import SseChunkStreamingResponse

# router = APIRouter(prefix="/api/openai/v1", tags=["openai"])
openai_app = FastAPI()
openai_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llmTransferService: LlmTransferService = OpenAiChatCompletionsService()


@openai_app.post(
    "/chat/completions",
    dependencies=[Depends(auth.header_authorize_check)]
)
async def chat_completions(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks
):
    """
    OpenAI Chat Completions API
    """
    context = cast(LlmRequestContext, request.state.context)
    provider_resp = await llmTransferService.run(context)
    # 消息返回后执行后续计费和日志存档任务
    background_tasks.add_task(llmTransferService.after_call_backend, context)
    # 按是否流式组织响应
    if context.is_stream:
        # EventSourceResponse
        return SseChunkStreamingResponse(
            llmTransferService.stream_generator(provider_resp, request.state.context),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Request-Id": context.letsgen_req_id,
                "qtraceid": context.trace_id,
            }
        )
    else:
        response.headers["X-Request-Id"] = context.letsgen_req_id
        response.headers["qtraceid"] = context.trace_id
        return provider_resp


# for debug purpose
@openai_app.get("/chat/completion")
async def get_chat_completions(account: str, model: str, duration: float = 1):
    """模拟耗时任务"""
    await asyncio.sleep(duration)
    return {"ok": True, "account": account, "model": model, "duration": duration}
