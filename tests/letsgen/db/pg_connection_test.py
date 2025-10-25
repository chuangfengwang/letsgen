# -*- coding: utf-8 -*-
"""
# @File    : pg_connection_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 21:07
"""
import asyncio

from letsgen.db.pg_connection import *
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def pg_connection_test():
    # 使用 dsn 参数传递完整的连接 URL
    db_pool = await async_db_pg_pool()
    log_pool = await async_log_pg_pool()
    db_engine = await async_db_pg_engine()
    log_engine = await async_log_pg_engine()

    # 从连接池获取一个连接
    async with db_pool.acquire() as connection:
        result = await connection.fetchval("SELECT 1 + 1")
        print(f"Result: {result}")

    async with log_pool.acquire() as connection:
        result = await connection.fetchval("SELECT 1 + 1")
        print(f"Result: {result}")

    # 使用 sqlalchemy engine 执行查询
    async with db_engine.connect() as conn:
        result = await conn.execute(text("SELECT cast(:a as INTEGER) + cast(:b as INTEGER)"), {"a": 1, "b": 2})
        print(result.fetchall())

    AsyncSessionLocal = async_sessionmaker(bind=log_engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT cast(:a as INTEGER) + cast(:b as INTEGER)"), {"a": 1, "b": 2})
        print(result.fetchall())

    # 关闭连接池
    await close_pg_pool()


if __name__ == "__main__":
    asyncio.run(pg_connection_test())
