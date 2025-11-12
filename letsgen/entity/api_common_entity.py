# -*- coding: utf-8 -*-
"""
# @File    : api_common_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-10 22:56
"""
from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class UiUserRoleEnum(str, Enum):
    """Ui user 角色"""
    # 成员名 = 成员值 (实际的字符串)
    normal = "normal"
    admin = "admin"


class UserToAccountRoleEnum(str, Enum):
    """ui user 对 account 的所有权角色"""
    normal = "normal"
    admin = "admin"


class UiUserStatusEnum(str, Enum):
    """Ui user 状态"""
    # 成员名 = 成员值 (实际的字符串)
    ok = "ok"
    disabled = "disabled"


class BillAccountStatusEnum(str, Enum):
    """bill account 状态"""
    ok = "ok"
    disabled = "disabled"


class WalletStatusEnum(str, Enum):
    """ wallet 状态"""
    ok = "ok"
    disabled = "disabled"


class ApikeyStatusEnum(str, Enum):
    """apikey 状态"""
    ok = "ok"
    disabled = "disabled"


class CurrencyTypeEnum(str, Enum):
    """货币类型枚举"""
    CNY = "CNY"
    USD = "USD"
    EUR = "EUR"


class BillAccountForm(BaseModel):
    account_name: str = Field(min_length=2, max_length=50)
    account_status: BillAccountStatusEnum = BillAccountStatusEnum.ok
    note: str | None = None


class ApiKeyForm(BaseModel):
    account_name: str = Field(min_length=2, max_length=50)
    apikey_name: str = Field(min_length=2, max_length=50)
    note: str | None = None


class WalletForm(BaseModel):
    account_name: str = Field(min_length=2, max_length=50)
    currency_type: CurrencyTypeEnum
    charge_delta: Decimal | None = Field(default=None)
    wallet_status: WalletStatusEnum = WalletStatusEnum.ok
    note: str | None = None
