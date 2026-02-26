# -*- coding: utf-8 -*-
"""
# @File    : number_util.py
# @Desc    : 数值相关的工具函数
# @Author  : chuangfeng.wang
# @Time    : 2026-02-27 02:08
"""
from decimal import Decimal, ROUND_HALF_UP


def float_to_decimal(f, precision=12):
    """
    将float转换为指定精度的Decimal
    """
    # 1. 必须先转 str，防止float本身的精度误差引入Decimal
    # 2. 使用 quantize 进行四舍五入
    target_pattern = Decimal('1.' + '0' * precision) if precision > 0 else Decimal('1')
    return Decimal(str(f)).quantize(target_pattern, rounding=ROUND_HALF_UP)
