# -*- coding: utf-8 -*-
"""
# @File    : app_lifespan.py
# @Desc    : 定义 app 声明周期上下文
# @Author  : chuangfeng.wang
# @Time    : 2025-11-15 22:59
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

import letsgen.db.pg_connection as db_pg_connection
import letsgen.middlewares.distributed_concurrency as distributed_concurrency

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

    SQLModel.metadata.clear()

    logger.info("Letsgen service end...")
