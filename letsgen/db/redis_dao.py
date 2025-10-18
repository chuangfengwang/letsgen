# -*- coding: utf-8 -*-
"""
# @File    : redis_dao.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 14:16
"""
import letsgen.db.redis_connetion as redis_connection
import letsgen.config as config

from redis.asyncio import StrictRedis as AsyncStrictRedis
from redis import StrictRedis as SyncStrictRedis

# 全局 redis 连接池
sync_redis_conn = None
async_redis_conn = None


def get_sync_redis_conn() -> SyncStrictRedis:
    """获取同步 redis 连接"""
    global sync_redis_conn
    if sync_redis_conn is not None:
        return sync_redis_conn
    if config.redis_conn_type == "single":
        sync_redis_conn = redis_connection.sync_single_conn(config.redis_single_url)
    return sync_redis_conn


def get_async_redis_conn() -> AsyncStrictRedis:
    """获取异步 redis 连接"""
    global async_redis_conn
    if async_redis_conn is not None:
        return async_redis_conn
    if config.redis_conn_type == "single":
        async_redis_conn = redis_connection.async_single_conn(config.redis_single_url)
    return async_redis_conn
