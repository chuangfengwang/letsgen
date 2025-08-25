# -*- coding: utf-8 -*-
"""
# @File    : auth.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-23 01:40
"""
from __future__ import annotations

import datetime
from typing import Annotated

from fastapi import HTTPException, Cookie, Header
from fastapi import status
from pydantic import BaseModel

import letsgen.utils.util as util


class LetsgenCookies(BaseModel):
    jwt: str | None = None


class LetsgenHeaders(BaseModel):
    authorization: str | None = None
    qtraceid: str | None = None


class Identity(BaseModel):
    user_name: str | None = None
    account_name: str | None = None
    qtraceid: str | None


async def user_authorize_check(
    cookies: Annotated[LetsgenCookies, Cookie()] = None,
) -> Identity:
    """
    UI 使用的 api cookie 检查
    """
    if not cookies.jwt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    return Identity(
        user_name="wcf",
        account_name="wcf_account",
        qtraceid=util.gen_uuid()
    )


async def any_authorize_check(
    cookies: Annotated[LetsgenCookies, Cookie()] = None,
    headers: Annotated[LetsgenHeaders, Header()] = None,
) -> Identity:
    """
    授权检查依赖函数. LLM api 用 cookie 或 header 中的 token 进行授权
    """
    if not cookies.jwt and not headers.authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    return Identity(
        user_name="wcf",
        account_name="wcf_account",
        qtraceid=headers.qtraceid if headers and headers.qtraceid else util.gen_uuid()
    )

