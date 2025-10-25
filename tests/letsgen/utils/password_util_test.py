# -*- coding: utf-8 -*-
"""
# @File    : password_util_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 22:34
"""
from letsgen.utils.password_util import *


def test_hash_password():
    # 测试哈希和验证功能
    password = "my_secure_password"
    hashed = hash_password(password)
    print("\n")
    assert verify_password(password, hashed) is True
    print("\n")
    assert verify_password("wrong_password", hashed) is False
