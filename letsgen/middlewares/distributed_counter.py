# -*- coding: utf-8 -*-
"""
# @File    : distribute_counter.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-13 20:56
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Tuple

from redis.asyncio import StrictRedis as AsyncStrictRedis


class Counter(ABC):
    """计数器抽象类"""

    @abstractmethod
    def build_key(self, keep_duration_num: int = 1) -> Tuple[str, int]:
        """构造周期代号
        :keep_duration_num: 计数值保持几个周期
        :return: (周期代号,过期时间毫秒时间戳)
        """
        ...

    @abstractmethod
    async def incr_count(self, delta: int = 1) -> Tuple[str, int]:
        """增加计数,返回(计数值,周期代号标记)"""
        ...

    @abstractmethod
    async def current_count(self, key: str = None) -> Tuple[int, str]:
        """查询指定周期 key 下的计数, 如果不提供key, 则用当前时间构造"""
        ...


class RedisPeriodCounter(Counter):
    """redis 周期内计数器"""
    # 周期轮转的锚点时间
    anchor_dt = datetime(2000, 1, 1)

    def __init__(self, redis_conn: AsyncStrictRedis, control_dim: str, duration_ms: int):
        self.redis_conn = redis_conn
        self.control_dim = control_dim
        # 计数统计时间周期
        self.duration_ms: int = duration_ms

    def build_key(self, keep_duration_num: int = 1) -> Tuple[str, int]:
        now = datetime.now()

        delta_ms = int((now - RedisPeriodCounter.anchor_dt).total_seconds() * 1000)
        duration_num = delta_ms // self.duration_ms

        expire_at_ms_dt = RedisPeriodCounter.anchor_dt + \
                          timedelta(milliseconds=(duration_num + keep_duration_num) * self.duration_ms)
        expire_at_ms = int(expire_at_ms_dt.timestamp() * 1000)

        return f"{self.control_dim}:{duration_num}", expire_at_ms

    async def incr_count(self, delta: int = 1) -> Tuple[int, str]:
        """增加计数"""
        key, expire_at_ms = self.build_key()
        count = await self.redis_conn.incrby(key, delta)
        await self.redis_conn.pexpireat(key, expire_at_ms)
        return count, key

    async def current_count(self, key: str = None) -> Tuple[int, str]:
        """获取计数值 和 计数key"""
        if not key:
            key, _ = self.build_key()
        count = await self.redis_conn.get(key)
        if count is not None:
            return int(count), key
        else:
            return 0, key


class PeriodAllCounterContext:
    """周期内计数上下文管理器: 进入时获得计数, 退出时总是计数"""

    def __init__(self, counter: Counter):
        self.counter = counter
        self.key = None

    async def __aenter__(self):
        """进入上下文管理器, 获得计数值"""
        cur_count, self.key = await self.counter.current_count()
        return cur_count, self.key

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器时, 根据是否有异常增加计数"""
        # 无论是否有异常，计数总加一
        self.key = await self.counter.incr_count(1)


class PeriodSuccessCounterContext:
    """周期内计数上下文管理器: 进入时获得计数, 成功退出时才计数"""

    def __init__(self, counter: Counter):
        self.counter = counter

    async def __aenter__(self):
        """进入上下文管理器, 获得计数值"""
        cur_count, self.key = await self.counter.current_count()
        return cur_count, self.key

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器时, 没有异常时, 增加计数"""
        if exc_type is None:
            # 没有异常，计数加一
            self.key = await self.counter.incr_count(1)
        # 其他情况, 不增加计数, 异常传递到外层
