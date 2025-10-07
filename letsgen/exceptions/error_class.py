# -*- coding: utf-8 -*-
"""
# @File    : error_class.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 22:14
"""
from http.server import BaseHTTPRequestHandler


class LetsgenError(Exception):
    """
    基础异常类
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class AuthorizationError(LetsgenError):
    """鉴权异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ParamError(LetsgenError):
    """参数异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)