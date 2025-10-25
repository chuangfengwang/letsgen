# -*- coding: utf-8 -*-
"""
# @File    : datatime_util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 22:16
"""
from datetime import datetime, timedelta


def current_time_str() -> str:
    """获取当前时间的字符串表示"""
    dt = datetime.now()
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")


def datetime_to_str(dt: datetime) -> str:
    """将 datetime 转换为字符串"""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")


def timedelta_to_milliseconds(td: timedelta) -> int:
    """将 timedelta 转换为毫秒数"""
    return int(td.total_seconds() * 1000)
