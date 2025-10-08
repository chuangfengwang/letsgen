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

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

import letsgen.config as config
import letsgen.log.concurrent_log as concurrent_log
import letsgen.middlewares.distributed_concurrency as distributed_concurrency
import letsgen.middlewares.e2e_tracelog_middleware as e2e_tracelog_middleware
import letsgen.routers.api_sys_router as api_sys_router
import letsgen.routers.openai_router as openai_router
import letsgen.routers.prometheus_router as prometheus_router
import letsgen.routers.sys_router as sys_router
import letsgen.routers.ui_router as ui_router

logging.config.dictConfig(concurrent_log.UVICORN_LOGGING_CONFIG)

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

    logger.info("Letsgen service end...")


app = FastAPI(
    title="Letsgen gateway",
    description="LLM API Gateway",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(e2e_tracelog_middleware.RequestResponseLogger)
app.add_middleware(distributed_concurrency.ConcurrencyLimitMiddleware)
# 系统级路径
app.include_router(sys_router.router)
# api 相关的系统状态接口
app.include_router(api_sys_router.router)
# openai 兼容接口
app.include_router(openai_router.router)
# UI 用到的接口
app.include_router(ui_router.router)

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
    message = f'Letsgen service error'
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"message": message}})


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
        # access_log=False,  # 使用自定义日志
        log_config=concurrent_log.UVICORN_LOGGING_CONFIG,  # 禁用默认日志配置
    )
