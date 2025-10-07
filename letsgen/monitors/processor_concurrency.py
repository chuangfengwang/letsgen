# -*- coding: utf-8 -*-
"""
# @File    : concurrency_controller.py
# @Desc    : 进程内并发控制
# @Author  : chuangfeng.wang
# @Time    : 2025-08-23 02:00
"""
import asyncio
import functools
import logging
from typing import Dict, Callable

logger = logging.getLogger(__name__)


class InProcessorConcurrencyMonitor:
    """
    进程内异步并发计数器上下文管理器。
    用于跟踪特定指标的当前正在处理的请求数量。
    """

    def __init__(self, metric_name: str):
        self.metric_name = metric_name
        self._current_concurrency: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()

    async def __aenter__(self):
        """
        进入上下文时，增加并发计数。
        """
        async with self._lock:
            self._current_concurrency += 1
            logger.info(f"[{self.metric_name}] Request entered. Current concurrency: {self._current_concurrency}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时（无论成功或失败），减少并发计数。
        """
        async with self._lock:
            self._current_concurrency -= 1
            logger.info(f"[{self.metric_name}] Request exited. Current concurrency: {self._current_concurrency}")
        if exc_type:
            logger.error(f"[{self.metric_name}] Request exited with exception: {exc_val}",
                         exc_info=(exc_type, exc_val, exc_tb))

    async def get_current_concurrency(self) -> int:
        """
        获取当前的并发请求数。
        """
        async with self._lock:
            return self._current_concurrency


class GlobalMonitorRegistry:
    """
    全局监控器注册表，管理不同名称的 ConcurrencyMonitor 实例。
    """
    def __init__(self):
        self._monitors: Dict[str, InProcessorConcurrencyMonitor] = {}
        self._lock: asyncio.Lock = asyncio.Lock()  # 用于保护 _monitors 字典的并发访问

    async def get_monitor(self, metric_name: str) -> InProcessorConcurrencyMonitor:
        """
        根据 metric_name 获取或创建一个 ConcurrencyMonitor 实例。
        """
        async with self._lock:
            if metric_name not in self._monitors:
                self._monitors[metric_name] = InProcessorConcurrencyMonitor(metric_name)
            return self._monitors[metric_name]

    async def get_all_concurrency_metrics(self) -> Dict[str, int]:
        """
        获取所有已注册监控器的当前并发数。
        """
        results = {}
        async with self._lock:  # 锁定注册表，确保在迭代时字典不被修改
            for name, monitor in self._monitors.items():
                # 注意：monitor.get_current_concurrency() 内部已经有自己的锁了
                results[name] = await monitor.get_current_concurrency()
        return results


# 参数化的装饰器
def monitor_concurrency(metric_name: str):
    """
    一个异步装饰器工厂函数，用于监控特定API的并发数。
    metric_name: 用于区分不同接口的并发指标名。
    """

    def actual_decorator(func: Callable):
        # 被注解的函数名
        func_name = func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取或创建对应 metric_name 的 ConcurrencyMonitor 实例
            monitor = await global_monitor_registry.get_monitor(metric_name)
            async with monitor:
                return await func(*args, **kwargs)

        return wrapper

    return actual_decorator


# 创建一个全局的监控器注册表实例
global_monitor_registry = GlobalMonitorRegistry()
