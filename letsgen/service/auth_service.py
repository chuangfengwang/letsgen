# -*- coding: utf-8 -*-
"""
# @File    : auth_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 21:54
"""
import logging

from fastapi import Request

import letsgen.db.pg_db_dao as pg_db_dao
from letsgen.db.pg_db_entity_auto import LetsgenAccountApikey
from letsgen.exceptions import error_class

logger = logging.getLogger(__name__)


def get_bear_from_authorization(authorization: str) -> str:
    """从 Authorization 中解析出 bearer"""
    if authorization.startswith("Bearer "):
        bear_token = authorization.split(" ", maxsplit=1)[1]
        return bear_token
    raise error_class.LlmAuthorizationError(f"Authorization error!")


async def parse_bear_as_account(bearer_token: str) -> LetsgenAccountApikey:
    """校验 bear token, 如果成功, 返回账户名"""
    if not bearer_token:
        logger.error("Bearer authorization error! Empty bearer")
        raise error_class.LlmAuthorizationError(f"Authorization error")
    letsgen_apikey = await pg_db_dao.fetch_account_by_apikey(bearer_token)
    if not letsgen_apikey:
        logger.error("Bearer authorization error! Bearer is invalid")
        raise error_class.LlmAuthorizationError(f"Authorization error")
    return letsgen_apikey


def get_authorization(request: Request) -> str:
    """从 request 中获取 Authorization"""
    authorization = request.headers.get("Authorization", "")
    return authorization


async def get_account(request: Request) -> str:
    """从 request 中解析出计费账号"""
    authorization = get_authorization(request)
    bear_token = get_bear_from_authorization(authorization)
    letsgen_apikey = await parse_bear_as_account(bear_token)
    return letsgen_apikey.account_name
