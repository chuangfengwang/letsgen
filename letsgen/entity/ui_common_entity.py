# -*- coding: utf-8 -*-
"""
# @File    : ui_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-01 00:51
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Tuple, Dict, Any

from pydantic import BaseModel, ConfigDict


class UiBaseResponse(BaseModel):
    """Ui接口基础响应实体"""
    status: int = 0
    message: str | None = None
    data: Any | None = None


class UiUserRoleEnum(str, Enum):
    """Ui user 角色"""
    # 成员名 = 成员值 (实际的字符串)
    normal = "normal"
    admin = "admin"


class UiUserStatusEnum(str, Enum):
    """Ui user 状态"""
    # 成员名 = 成员值 (实际的字符串)
    ok = "ok"
    disabled = "disabled"
