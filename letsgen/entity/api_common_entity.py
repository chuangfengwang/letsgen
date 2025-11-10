# -*- coding: utf-8 -*-
"""
# @File    : api_common_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-10 22:56
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class BillAccountStatusEnum(str, Enum):
    """bill account 状态"""
    ok = "ok"
    disabled = "disabled"


class BillAccountForm(BaseModel):
    account_name: str = Field(min_length=2, max_length=50)
    account_status: BillAccountStatusEnum = BillAccountStatusEnum.ok
    note: str | None = None
