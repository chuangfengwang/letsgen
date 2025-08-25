#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : letsgen_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:30
"""
import os
import sys

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import letsgen.config as config
import letsgen.routers.sys_router as sys_router
import letsgen.routers.prometheus_router as prometheus_router
import letsgen.routers.openai_router as openai_router
import letsgen.routers.ui_router as ui_router
import letsgen.middlewares.e2e_tracelog_middleware as e2e_tracelog_middleware

# 确保当前目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
app = FastAPI()

app.add_middleware(e2e_tracelog_middleware.RequestResponseLogger)
app.include_router(sys_router.router)
app.include_router(openai_router.router)
app.include_router(ui_router.router)

app.mount("/ui", StaticFiles(directory=config.ui_static_dir), name="ui_static")
app.mount("/metrics", prometheus_router.prometheus_metrics_app, name="prometheus_metrics")

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
    )
