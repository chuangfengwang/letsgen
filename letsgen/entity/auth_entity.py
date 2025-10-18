# -*- coding: utf-8 -*-
"""
# @File    : auth_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-08 19:46
"""
from __future__ import annotations

from pydantic import BaseModel


class LetsgenCookies(BaseModel):
    jwt: str | None = None


class LetsgenHeaders(BaseModel):
    authorization: str | None = None


class Identity(BaseModel):
    user_name: str | None = None
    account_name: str | None = None
