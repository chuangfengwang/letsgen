#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : letsgen_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:30
"""
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import letsgen.config as config
import letsgen.routers.sys_router as sys_router

app = FastAPI()
app.include_router(sys_router.router)
app.mount("/ui", StaticFiles(directory=config.ui_static_dir), name="ui_static")

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
