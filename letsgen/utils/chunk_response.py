# -*- coding: utf-8 -*-
"""
# @File    : chunk_response.py
# @Desc    :
# @Author  : chuangfeng.wang
# @Time    : 2025-11-12 15:57
"""
from typing import AsyncIterable, Awaitable, Callable, Optional
from fastapi.responses import StreamingResponse


class SseChunkStreamingResponse(StreamingResponse):
    """支持流结束回调的自定义 StreamingResponse"""

    def __init__(
        self, content: AsyncIterable, *args,
        on_complete: Optional[Callable[[], Awaitable[None]]] = None,
        **kwargs):
        # 包装 content 生成器以支持 on_complete 回调
        if on_complete:
            content = self._wrap_with_callback(content, on_complete)
        super().__init__(content, *args, **kwargs)

    @staticmethod
    async def _wrap_with_callback(
        content: AsyncIterable,
        on_complete: Callable[[], Awaitable[None]]
    ) -> AsyncIterable:
        """包装内容生成器，在流结束时执行回调"""
        try:
            async for chunk in content:
                yield chunk
        finally:
            await on_complete()
