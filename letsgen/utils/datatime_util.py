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


def parse_time(time_str: str) -> int:
    """
    解析时间字符串, 转换为秒数
    :param time_str: 时间字符串, 例如 "5m" (5分钟), "1h" (1小时)
    :return: 秒数
    """
    time_str = time_str.strip().lower()
    if time_str == "inf":
        return int('inf')

    time_units = {
        's': 1,  # 秒
        'm': 60,  # 分钟
        'h': 3600,  # 小时
        'd': 86400,  # 天
    }

    for suffix, multiplier in time_units.items():
        if time_str.endswith(suffix):
            return int(time_str[:-1]) * multiplier

    # 如果没有单位, 默认按秒处理
    return int(time_str)
