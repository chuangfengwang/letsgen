# -*- coding: utf-8 -*-
"""
# @File    : auth.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-23 01:40
"""
from __future__ import annotations

from typing import Annotated, cast

from fastapi import HTTPException, Cookie, Header
from fastapi import status
from starlette.requests import Request

from exceptions import error_class
from letsgen.entity.auth_entity import (LetsgenCookies, LetsgenHeaders, Identity)
from letsgen.entity.llm_entity import (LlmRequestContext)
from letsgen.service.ui_normal_service import UiNormalService
import letsgen.service.auth_service as auth_service

ui_normal_service = UiNormalService()


async def jwt_authorize_check(
    request: Request,
    cookies: Annotated[LetsgenCookies, Cookie()] = None,
) -> Identity:
    """
    UI 使用的 api cookie 检查: jwt
    """
    if not cookies.jwt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")

    identity = ui_normal_service.check_jwt(cookies.jwt)

    context = cast(LlmRequestContext, request.state.context)
    context.identity = identity
    return identity


async def header_authorize_check(
    request: Request,
    headers: Annotated[LetsgenHeaders, Header()] = None,
) -> Identity:
    """
    授权检查依赖函数. LLM api 用 header 中的 authorization bear token 进行授权
    """
    # 解析 bearer, 必须有
    bearer = auth_service.get_bear_from_authorization(headers.authorization)
    letsgen_apikey = await auth_service.parse_bear_as_account(bearer)
    # 解析 jwt, 可有可无
    jwt_identity = None
    if "jwt" in request.cookies:
        try:
            jwt_identity = ui_normal_service.check_jwt(request.cookies.get("jwt"))
        except Exception:
            jwt_identity = None
    # 构造 identity
    identity = Identity(
        user_name=jwt_identity.user_name if jwt_identity else None,
        roles=jwt_identity.roles if jwt_identity else [],
        account_name=letsgen_apikey.account_name,
    )
    context = cast(LlmRequestContext, request.state.context)
    context.identity = identity
    return identity
