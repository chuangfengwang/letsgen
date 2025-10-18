# -*- coding: utf-8 -*-
"""
# @File    : function_util_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-18 22:48
"""
from letsgen.utils.function_util import *


def my_function(a, b=10, *, c, **kwargs):
    """一个包含不同类型参数的示例函数"""
    pass


class TestClassFunction:
    def method(self, a, b=10, *, c, **kwargs):
        pass


def test_all_param_expect_kwargs():
    params = all_param_expect_kwargs(my_function)
    expected_params = ['a', 'b', 'c']
    assert params == expected_params, f"Expected {expected_params}, but got {params}"


def test_all_param_expect_kwargs2():
    func_obj = TestClassFunction()
    params = all_param_expect_kwargs(func_obj.method)
    print(params)
    expected_params = ['a', 'b', 'c']
    assert params == expected_params, f"Expected {expected_params}, but got {params}"


def test_all_param_expect_kwargs3():
    params = all_param_expect_kwargs(TestClassFunction.method)
    print(params)
    expected_params = ['self', 'a', 'b', 'c']
    assert params == expected_params, f"Expected {expected_params}, but got {params}"
