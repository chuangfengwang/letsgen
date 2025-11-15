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
from letsgen.entity.api_common_entity import UiUserRoleEnum, UiUserStatusEnum, EndpointStatusEnum, \
    EndpointApiFormatEnum, CredentialType, CredentialStatus


class FirstAdminUser(BaseModel):
    """第一个 admin 用户表单"""
    user_name: str = Field(min_length=2, max_length=50)
    password_plain: str = Field(min_length=6, max_length=64)
    user_email: str | None = None
    user_phone: str | None = None


class UserForm(BaseModel):
    """用户实体表单"""
    user_name: str = Field(min_length=2, max_length=50)
    user_email: str | None = None
    password_plain: str = Field(min_length=6, max_length=64)
    user_phone: str | None = None
    ui_role: UiUserRoleEnum = UiUserRoleEnum.normal
    user_status: UiUserStatusEnum = UiUserStatusEnum.ok
    note: str | None = None


class CredentialForm(BaseModel):
    """凭证表单"""
    provider_name: str = Field(min_length=1, max_length=50)
    credential_name: str = Field(min_length=2, max_length=50)
    credential_type: CredentialType = CredentialType.apiKey
    credential_value: str = ""
    credential_status: CredentialStatus = CredentialStatus.ok
    expire_at: datetime | None = None
    note: str = ""


class EndpointForm(BaseModel):
    """Endpoint 表单"""
    provider_name: str = Field(min_length=1, max_length=50)
    endpoint_name: str = Field(min_length=2, max_length=50)
    credential_name1: str | None = Field(min_length=2, max_length=50)
    credential_name2: str | None = Field(min_length=2, max_length=50)
    endpoint_status: EndpointStatusEnum = EndpointStatusEnum.ok
    endpoint_baseurl: str = Field(min_length=7, max_length=1024)
    endpoint_region: str | None = Field(min_length=2, max_length=50)
    endpoint_proxies: str = ""
    api_format: EndpointApiFormatEnum = EndpointApiFormatEnum.openai
    endpoint_path_info: str = ""
    endpoint_quota: str = ""
    note: str = ""
