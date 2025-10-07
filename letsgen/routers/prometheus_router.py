# -*- coding: utf-8 -*-
"""
# @File    : prometheus_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:43
"""
from fastapi import APIRouter
from prometheus_client import CollectorRegistry
from prometheus_client import multiprocess, make_asgi_app

router = APIRouter(tags=["prometheus"])


def make_metrics_app():
    """创建多进程兼容实例"""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)
