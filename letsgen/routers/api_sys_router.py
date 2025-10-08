# -*- coding: utf-8 -*-
"""
# @File    : api_sys_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 23:35
"""
from typing import Dict

from fastapi import APIRouter

import letsgen.middlewares.distributed_concurrency as distributed_concurrency
import letsgen.utils.util as util
import letsgen.monitors.processor_concurrency as processor_concurrency

router = APIRouter(prefix="/api/sys", tags=["api_sys"])


# todo: 鉴权
@router.get("/concurrency/account/{account}")
async def account_concurrency(account: str, model_id: str):
    """查询某个账户指定模型的并发数"""
    counter = distributed_concurrency.ConcurrencyLimitMiddleware.get_counter()
    control_key = f"{account}-{model_id}"
    now_str = util.current_time_str()
    concurrency = await counter.fetch_request_concurrency(control_key)
    return {"query_time": now_str, "account": account, "model_id": model_id, "concurrency": concurrency}


@router.get("/concurrency/inRedisInstances")
async def in_redis_instances():
    """查询所有实例列表"""
    counter = distributed_concurrency.ConcurrencyLimitMiddleware.get_counter()
    now_str = util.current_time_str()
    instances = await counter.fetch_alive_instances()
    return {"query_time": now_str, "instances": instances}


@router.get("/concurrency/allInstanceConcurrency")
async def all_instance_concurrency():
    """查询所有实例的并发数（所有用户所有模型总和）"""
    counter = distributed_concurrency.ConcurrencyLimitMiddleware.get_counter()
    now_str = util.current_time_str()
    instance_concurrency_dict: Dict[str, int] = await counter.fetch_all_instance_currency()
    total = 0
    for value in instance_concurrency_dict.values():
        total += value
    return {"query_time": now_str, "total": total, "instance_concurrency": instance_concurrency_dict}


@router.get("/concurrency/inProcessMetrics")
async def get_all_concurrency_metrics():
    """
    获取当前进程内所有已注册的并发指标及它们当前的并发数。
    """
    now_str = util.current_time_str()
    all_metrics = await processor_concurrency.global_monitor_registry.get_all_concurrency_metrics()
    return {"query_time": now_str, "concurrency_metrics": all_metrics}
