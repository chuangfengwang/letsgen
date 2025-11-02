# -*- coding: utf-8 -*-
"""
# @File    : ui_admin_router_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-01 22:39
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


class FirstAdminUser(BaseModel):
    """第一个 admin 用户实体"""
    user_name: str = Field(min_length=2, max_length=50)
    password_plain: str = Field(min_length=6, max_length=64)
    user_email: str | None = None
    user_phone: str | None = None
