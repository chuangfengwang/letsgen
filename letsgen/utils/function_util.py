# -*- coding: utf-8 -*-
"""
# @File    : function_util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-18 22:35
"""

import inspect
from typing import Callable, List


def all_param_expect_kwargs(func: Callable) -> List[str]:
    """获取除可变关键字参数之外的所有参数名"""
    # 1. 获取函数的 Signature 对象
    sig = inspect.signature(func)

    # 2. 获取参数的有序映射（OrderedDict. key:参数名, value:inspect.Parameter）
    parameters = sig.parameters

    # 过滤参数名
    non_var_keyword_params = [
        name for name, param in parameters.items()
        if param.kind != inspect.Parameter.VAR_KEYWORD
    ]
    return non_var_keyword_params
