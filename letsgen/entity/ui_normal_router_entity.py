# -*- coding: utf-8 -*-
"""
# @File    : ui_normal_router_entity.py
# @Desc    :
# @Author  : chuangfeng.wang
# @Time    : 2025-11-02 20:27
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


class LoginEntity(BaseModel):
    """登录实体"""
    user_name: str = Field(min_length=2, max_length=50)
    password_plain: str = Field(min_length=6, max_length=64)


class RegisterUserEntity(BaseModel):
    """用户注册表单"""
    user_name: str = Field(min_length=2, max_length=50)
    password_plain: str = Field(min_length=6, max_length=64)
    user_email: str | None = None
    user_phone: str | None = None
