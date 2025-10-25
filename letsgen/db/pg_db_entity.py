# -*- coding: utf-8 -*-
"""
# @File    : pg_db_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 21:55
"""
from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    """用户实体类"""
    id: int | None
    user_name: str
    user_email: str | None
    user_password: str | None
    user_password_plain: str | None
    user_phone: str | None
    ui_role: str | None
    user_status: str | None
    note: str | None
    create_at: datetime.datetime | None
    update_at: datetime.datetime | None

    # 启用 from_attributes
    model_config = ConfigDict(from_attributes=True)
