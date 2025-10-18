# -*- coding: utf-8 -*-
"""
# @File    : auth_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 21:54
"""
from fastapi import Request

from letsgen.exceptions import error_class


def get_bear(request: Request) -> str:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("bear "):
        bear_token = authorization.split(" ", maxsplit=1)[1]
        return bear_token
    raise error_class.AuthorizationError(f"bear error!")


async def check_and_parse_bear(bear_token: str) -> str:
    """校验 bear token, 如果成功, 返回账户名"""

    return "wcf"


async def get_account(request: Request) -> str:
    try:
        bear_token = get_bear(request)
        account = await check_and_parse_bear(bear_token)
        return account
    except Exception as e:
        # todo: debug
        account = request.query_params.get("account", "")
        if not account:
            raise error_class.AuthorizationError(f"debug account error!")
        return account
