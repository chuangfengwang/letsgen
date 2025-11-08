#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : letsgen_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:30
"""
import json
import logging.config
import os
from contextlib import asynccontextmanager
from json import JSONDecodeError
from typing import cast

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

import letsgen.config as config
import letsgen.db.pg_connection as db_pg_connection
import letsgen.exceptions.error_class as error_class
import letsgen.log.concurrent_log as concurrent_log
import letsgen.middlewares.distributed_concurrency as distributed_concurrency
import letsgen.middlewares.e2e_tracelog_middleware as e2e_tracelog_middleware
import letsgen.routers.api_sys_router as api_sys_router
import letsgen.routers.openai_router as openai_router
import letsgen.routers.prometheus_router as prometheus_router
import letsgen.routers.sys_router as sys_router
import letsgen.routers.ui_admin_router as ui_admin_router
import letsgen.routers.ui_normal_router as ui_normal_router
import letsgen.routers.ui_sys_router as ui_sys_router
from letsgen.entity.llm_entity import LlmRequestContext

# logging.config.dictConfig(concurrent_log.UVICORN_LOGGING_CONFIG)

logger = logging.getLogger(__name__)
dw_logger = logging.getLogger("data-warehouse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Letsgen service start...")
    dw_logger.info("data warehouse log info...")

    # 向 redis 发送心跳信号任务启动
    await distributed_concurrency.ConcurrencyLimitMiddleware.cls_async_init()

    yield

    # 向 redis 发送心跳信号任务停止
    await distributed_concurrency.ConcurrencyLimitMiddleware.cls_async_close()
    await db_pg_connection.close_pg_pool()

    logger.info("Letsgen service end...")


app = FastAPI(
    title="Letsgen gateway",
    description="LLM API Gateway",
    version="0.1.0",
    lifespan=lifespan
)

# 中间件: 最后添加的最先执行
app.add_middleware(distributed_concurrency.ConcurrencyLimitMiddleware)
app.add_middleware(e2e_tracelog_middleware.RequestResponseLogger)

# 系统级路径
app.include_router(sys_router.router)
# api 相关的系统状态接口
app.include_router(api_sys_router.router)
# openai 兼容接口
app.include_router(openai_router.router)
# UI 用到的接口
app.include_router(ui_admin_router.router)
app.include_router(ui_normal_router.router)
app.include_router(ui_sys_router.router)

# 前端/静态资源
app.mount("/ui", StaticFiles(directory=config.ui_static_dir), name="ui_static")
# prometheus 监控端点
app.mount("/metrics", prometheus_router.make_metrics_app(), name="prometheus_metrics")


# 捕获所有未处理的异常
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 安全获取请求体数据
    body_bytes = None
    try:
        if request.method in ("POST", "PUT", "PATCH"):
            body_bytes = await request.body()
            json.loads(body_bytes)  # 尝试解析验证
    except (JSONDecodeError, UnicodeDecodeError):
        body_bytes = b"<invalid JSON>"
    except Exception:
        body_bytes = b"<unreadable body>"
    logger.error(f"Letsgen error. path: {request.url.path}, method: {request.method}, body_bytes: {body_bytes}",
                 exc_info=True)
    context = cast(LlmRequestContext, request.state.context)
    error_info = {"letsgen_req_id": context.letsgen_req_id, "qtraceid": context.trace_id}
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


if __name__ == '__main__':
    import uvicorn

    service = os.path.basename(__file__)[:-3]
    # 启动服务
    uvicorn.run(
        f"{service}:app",
        host="0.0.0.0",
        port=config.letsgen_web_port,
        workers=config.letsgen_workers,
        timeout_keep_alive=config.timeout_keep_alive,
        limit_max_requests=None,  # 不限制请求数
        # access_log=False,  # 禁用 access 日志
        proxy_headers=True,  # 启用 X-Forwarded-For 支持
        forwarded_allow_ips="192.168.0.0/16,172.16.0.0/12,10.0.0.0/8,127.0.0.1,[::1]",  # 信任反代ip范围为局域网 ip
        log_config=concurrent_log.UVICORN_LOGGING_CONFIG,  # 禁用默认日志配置
    )
