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
from letsgen.system.global_service import llmTransferService, log_content_service
from letsgen.db.minio_dao import close_minio_client

logger = logging.getLogger(__name__)
dw_logger = logging.getLogger("data-warehouse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Letsgen service start...")
    dw_logger.info("data warehouse log info...")

    # 向 redis 发送心跳信号任务启动
    await distributed_concurrency.ConcurrencyLimitMiddleware.cls_async_init()
    await log_content_service.async_init()
    # 最后是 api 接口功能初始化
    await llmTransferService.async_init()

    yield

    await close_minio_client()
    await db_pg_connection.close_pg_pool()
    # 向 redis 发送心跳信号任务停止
    await distributed_concurrency.ConcurrencyLimitMiddleware.cls_async_close()

    SQLModel.metadata.clear()

    logger.info("Letsgen service end...")
