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

from letsgen.entity.auth_entity import (LetsgenCookies, LetsgenHeaders, Identity)
from letsgen.entity.llm_entity import (LlmRequestContext)


async def jwt_authorize_check(
    request: Request,
    cookies: Annotated[LetsgenCookies, Cookie()] = None,
) -> Identity:
    """
    UI 使用的 api cookie 检查: jwt
    """
    if not cookies.jwt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    identity = Identity(
        user_name="wcf",
        account_name="wcf_account",
    )
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
    if not headers.authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    identity = Identity(
        user_name="wcf",
        account_name="wcf_account",
    )
    context = cast(LlmRequestContext, request.state.context)
    context.identity = identity
    return identity
