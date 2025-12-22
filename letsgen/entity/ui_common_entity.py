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

from pydantic import BaseModel, ConfigDict, Field


class UiBaseResponse(BaseModel):
    """Ui接口基础响应实体"""
    status: int = 0
    msg: str | None = None
    data: Any | None = None
