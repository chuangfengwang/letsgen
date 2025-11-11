# -*- coding: utf-8 -*-
"""
# @File    : pg_connection.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-26 00:45
"""
from typing import Optional

import asyncpg
from asyncpg.pool import Pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

import letsgen.config as config

# 全局 pg 数据库连接池
db_pg_pool: Optional[Pool] = None
log_pg_pool: Optional[Pool] = None
db_pg_engine: Optional[AsyncEngine] = None
log_pg_engine: Optional[AsyncEngine] = None


async def async_db_pg_pool() -> Pool:
    """获取 db pg 数据库连接池"""
    global db_pg_pool
    if db_pg_pool is not None:
        return db_pg_pool

    db_pg_pool = await asyncpg.create_pool(
        dsn=config.letsgen_db_pg_url,
        min_size=1,  # 最小连接数
        max_size=20,  # 最大连接数
    )
    return db_pg_pool


def build_sqlalchemy_url(pg_url: str) -> str:
    """构建 SQLAlchemy 连接 URL"""
    if pg_url.startswith("postgresql+asyncpg://"):
        return pg_url
    elif pg_url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + pg_url[len("postgresql://"):]
    else:
        raise ValueError("Invalid PostgreSQL URL format")


async def async_db_pg_engine() -> AsyncEngine:
    """获取 db pg 数据库连接池"""
    global db_pg_engine
    if db_pg_engine is not None:
        return db_pg_engine

    db_pg_engine = create_async_engine(
        build_sqlalchemy_url(config.letsgen_db_pg_url),
        pool_size=1,
        max_overflow=20,
        echo=config.debug_flag,
        connect_args={
            "server_settings": {
                "timezone": config.letsgen_pg_timezone
            }
        }
    )
    return db_pg_engine


async def async_log_pg_pool() -> Pool:
    """获取 log pg 数据库连接池"""
    global log_pg_pool
    if log_pg_pool is not None:
        return log_pg_pool

    log_pg_pool = await asyncpg.create_pool(
        dsn=config.letsgen_log_pg_url,
        min_size=1,  # 最小连接数
        max_size=10,  # 最大连接数
    )
    return log_pg_pool


async def async_log_pg_engine() -> AsyncEngine:
    """获取 db pg 数据库连接池"""
    global log_pg_engine
    if log_pg_engine is not None:
        return log_pg_engine

    log_pg_engine = create_async_engine(
        build_sqlalchemy_url(config.letsgen_log_pg_url),
        pool_size=1,
        max_overflow=20,
        echo=config.debug_flag,
        connect_args={
            "server_settings": {
                "timezone": config.letsgen_pg_timezone
            }
        }
    )
    return log_pg_engine


async def close_pg_pool():
    """关闭所有 pg 数据库连接池"""
    global db_pg_pool, log_pg_pool
    if db_pg_pool is not None:
        await db_pg_pool.close()
        db_pg_pool = None
    if log_pg_pool is not None:
        await log_pg_pool.close()
        log_pg_pool = None
    if db_pg_engine is not None:
        await db_pg_engine.dispose()
    if log_pg_engine is not None:
        await log_pg_engine.dispose()
