#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : letsgen_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:30
"""
import logging.config
import os

from fastapi.staticfiles import StaticFiles

import letsgen.config as config
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
from system.exception_handler import add_global_exception_handler
from system.make_config_app import make_app

# logging.config.dictConfig(concurrent_log.UVICORN_LOGGING_CONFIG)

logger = logging.getLogger(__name__)
dw_logger = logging.getLogger("data-warehouse")

# 生成经过配置的 app
app = make_app()

# 中间件: 最后添加的最先执行
app.add_middleware(distributed_concurrency.ConcurrencyLimitMiddleware)
app.add_middleware(e2e_tracelog_middleware.RequestResponseLogger)

# 系统级路径
app.include_router(sys_router.router)
# api 相关的系统状态接口
app.include_router(api_sys_router.router)
# UI 用到的接口
app.include_router(ui_admin_router.router)
app.include_router(ui_normal_router.router)
app.include_router(ui_sys_router.router)
# api 相关的系统状态接口
app.include_router(api_sys_router.router)

# openai 兼容接口
app.mount("/api/openai/v1", openai_router.openai_app)
# 前端/静态资源
app.mount("/ui", StaticFiles(directory=config.ui_static_dir), name="ui_static")
# prometheus 监控端点
app.mount("/metrics", prometheus_router.make_metrics_app(), name="prometheus_metrics")

# 添加全局异常处理
add_global_exception_handler(app)

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
