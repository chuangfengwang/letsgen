# -*- coding: utf-8 -*-
"""
# @File    : exception_handler.py
# @Desc    : 全局异常处理
# @Author  : chuangfeng.wang
# @Time    : 2025-11-15 22:54
"""
import logging
from typing import cast

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import FastAPI

from letsgen.entity.llm_entity import LlmRequestContext
import letsgen.exceptions.error_class as error_class

logger = logging.getLogger(__name__)


def add_global_exception_handler(app: FastAPI):
    # 捕获所有未处理的异常
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """统一异常捕获"""
        context = cast(LlmRequestContext, request.state.context)
        error_info = {"letsgen_req_id": context.letsgen_req_id, "qtraceid": context.trace_id}
        logger.error(f"Letsgen error. qtraceid: {context.trace_id}, letsgen_req_id: {context.letsgen_req_id}, "
                     f"path: {request.url.path}, method: {request.method}",
                     exc_info=True)
        headers = {"X-Request-Id": context.letsgen_req_id, "qtraceid": context.trace_id, }
        if hasattr(exc, "message"):
            error_info["message"] = exc.message
        else:
            message = f'Letsgen service error'
            error_info["message"] = message
        # 响应码
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if isinstance(exc, (error_class.UiAuthorizationError, error_class.LlmAuthorizationError)):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, (error_class.UiParamError, error_class.LlmParamError)):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, (error_class.ProviderRateLimitError,)):
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return JSONResponse(
            content={"error": error_info},
            headers=headers,
            status_code=status_code,
        )
