# -*- coding: utf-8 -*-
"""
# @File    : auth_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-08 19:46
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel


class LetsgenCookies(BaseModel):
    jwt: str | None = None


class LetsgenHeaders(BaseModel):
    authorization: str | None = None


class Identity(BaseModel):
    # user_name roles 用于 ui 交互
    user_name: str | None = None
    roles: List[str] = []
    # account_name 用户 api 交互
    account_name: str | None = None
