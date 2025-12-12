# -*- coding: utf-8 -*-
"""
# @File    : redis_dao_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-07 10:23
"""
from letsgen.db.redis_dao import *


def get_sync_redis_conn_test():
    conn = get_sync_redis_conn()
    conn.set("key-wcf", "syncTestValue")
    conn.close()


async def get_async_redis_conn_test():
    conn = get_async_redis_conn()
    await conn.set("key-wcf", "asyncTestValue")
    await conn.zadd("key-wcf-zset", {"member1": 1, "member2": 2})
    await conn.aclose()


if __name__ == '__main__':
    get_sync_redis_conn_test()

    import asyncio

    asyncio.run(get_async_redis_conn_test())
