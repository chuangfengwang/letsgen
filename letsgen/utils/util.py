#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-16 00:03
"""
import uuid
from datetime import datetime
import base64


def gen_uuid():
    """生成紧凑格式的 UUID"""
    uuid_output = str(uuid.uuid4()).replace("-", "")
    return uuid_output


def gen_uuid_base64() -> str:
    """生成 base64 格式的 UUID. 包含字符 + 和 / , 但不包含 = 号"""
    uuid_output = str(base64.b64encode(uuid.uuid4().bytes), 'utf-8').replace("=", "")
    return uuid_output


def _padding_to_base64(string: str) -> str:
    return string + "=" * (len(string) % 4)


def b64decode(string: str) -> bytes:
    """带 padding 补齐能力的 base64 解码器"""
    return base64.b64decode(_padding_to_base64(string).encode('utf-8'))


def current_time_str() -> str:
    dt = datetime.now()
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
