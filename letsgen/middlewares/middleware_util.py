# -*- coding: utf-8 -*-
"""
# @File    : middleware_util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 21:29
"""
import json
import sys

from fastapi import Request
from starlette.types import Message

import asyncio
from contextlib import asynccontextmanager


# 这是一个内部辅助函数，用于重新设置请求的接收流
async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    # 替换请求的 _receive 方法
    request._receive = receive


@asynccontextmanager
async def reconsume_json_body(request: Request):
    # 1. 检查方法：通常只有 POST/PUT/PATCH 等方法才有请求主体
    if request.method not in ["POST", "PUT", "PATCH"]:
        yield request.body()

    body = None
    try:
        # 2. 读取原始请求主体（字节）
        body = await request.body()
    except Exception as e:
        print(f"无法读取请求主体: {e}")
        # 即使读取失败，也应该继续处理请求

    try:
        yield body  # 资源在 'yield' 处返回，代码块执行
    finally:
        # --- 清理逻辑 (相当于 __aexit__) ---
        print("Exiting: Async cleanup started...")
        # 4. 关键步骤：重新设置请求主体
        # 这一步确保了路由处理函数可以再次读取主体
        await set_body(request, body)
        print("Cleanup complete.")
