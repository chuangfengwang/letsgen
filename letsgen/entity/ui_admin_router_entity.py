# -*- coding: utf-8 -*-
"""
# @File    : ui_admin_router_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-01 22:39
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Dict, Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from letsgen.entity.ui_common_entity import UiUserRoleEnum, UiUserStatusEnum


class FirstAdminUser(BaseModel):
    """第一个 admin 用户实体"""
    user_name: str = Field(min_length=2, max_length=50)
    password_plain: str = Field(min_length=6, max_length=64)
    user_email: str | None = None
    user_phone: str | None = None


class UserForm(BaseModel):
    """用户实体"""
    user_name: str = Field(min_length=2, max_length=50)
    user_email: str | None = None
    password_plain: str = Field(min_length=6, max_length=64)
    user_phone: str | None = None
    ui_role: UiUserRoleEnum = UiUserRoleEnum.normal
    user_status: UiUserStatusEnum = UiUserStatusEnum.ok
    note: str | None = None
