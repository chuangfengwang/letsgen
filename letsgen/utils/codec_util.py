#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-16 00:03
"""
import base64
import datetime
import json
import uuid
from dataclasses import is_dataclass, asdict
from enum import Enum

from pydantic import BaseModel


def gen_uuid():
    """生成紧凑格式的 UUID"""
    uuid_output = str(uuid.uuid4()).replace("-", "")
    return uuid_output


def gen_uuid_base64() -> str:
    """生成 base64 格式的 UUID. 包含字符 + 和 / , 但不包含 = 号"""
    uuid_output = str(base64.b64encode(uuid.uuid4().bytes), 'utf-8').rstrip("=")
    return uuid_output


def _padding_to_base64(string: str) -> str:
    """用 = 补齐 base64 字符串长度到 4 的倍数长度"""
    return string + "=" * (len(string) - len(string) % 4)


def b64decode(string: str) -> bytes:
    """带 padding 补齐能力的 base64 解码器"""
    return base64.b64decode(_padding_to_base64(string).encode('utf-8'))


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        # 有特殊格式化需求的类型处理
        if isinstance(obj, datetime.datetime):
            # 将 datetime 对象转换为 ISO 8601 格式的字符串 "2024-05-29T18:58:37.168222"
            return obj.isoformat()
        if isinstance(obj, Enum):
            # enum 类型处理: 枚举类型.枚举值
            return '%s.%s' % (obj.__class__.__name__, obj.name)
        # 其他 object 类型的处理
        elif isinstance(obj, object):
            # 读取对象的所有非私有属性
            d = {
                cls_attr: getattr(obj, cls_attr) for cls_attr in dir(obj) if
                not cls_attr.startswith("__")  # 实际上不会有, 因为 dir() 不会返回双下划线开头的属性
                and not cls_attr.startswith("_")
                and not callable(getattr(obj, cls_attr))
            }
            return d
        return super().default(obj)
