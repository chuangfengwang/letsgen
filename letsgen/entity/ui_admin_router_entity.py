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
    EndpointApiFormatEnum, CredentialType, CredentialStatus, ModelEndpointStatusEnum, ModelTypeEnum, ModelStatusEnum


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


class AddEndpointForModelForm(BaseModel):
    """给 model 添加 Endpoint 表单"""
    model_name: str = Field(min_length=2, max_length=50)
    provider_name: str = Field(min_length=1, max_length=50)
    endpoint_name: str = Field(min_length=2, max_length=50)
    provider_model_id: str = Field(min_length=1, max_length=50)
    provider_params: str | None = None
    m_edp_status: ModelEndpointStatusEnum = ModelEndpointStatusEnum.ok
    rpd_limit: int | None = None
    rpd_duration: int | None = None
    tpd_limit: int | None = None
    tpd_duration: int | None = None
    ifr_limit: int | None = None
    note: str = ""

class ModelForm(BaseModel):
    """模型表单"""
    model_name: str = Field(min_length=2, max_length=50, title="模型名称", description="模型名称，必填，长度2-50")
    model_type: ModelTypeEnum = Field(default=ModelTypeEnum.generate, title="模型类型", description="模型类型，枚举值：generate、embedding、rerank，默认值为 generate")
    model_status: ModelStatusEnum = Field(default=ModelStatusEnum.waiting, title="模型状态", description="模型状态，枚举值：waiting（上架中）、ok（正常）、deprecated（已废弃，不推荐使用但仍可用）、disabled（已禁用，不可用），默认值为 waiting")
    provider: str = Field(min_length=2, max_length=20, title="模型提供商", description="模型提供商名称，必填，长度2-20")
    support_tools: int = Field(title="是否支持 tools 调用", description="是否支持 tools 调用，枚举值：0（不支持）、1（支持），默认值为 1")
    support_non_stream: int = Field(title="是否支持非流式响应", description="是否支持非流式响应，枚举值：0（不支持）、1（支持），默认值为 1")
    support_stream: int = Field(title="是否支持流式响应", description="是否支持流式响应，枚举值：0（不支持）、1（支持），默认值为 1")
    support_reasoning: int = Field(title="是否支持推理", description="是否支持推理，枚举值：0（不支持）、1（支持），默认值为 0")
    input_modalities: str = Field(min_length=0, max_length=100, title="支持的输入模态", description="支持的输入模态，逗号分隔的字符串，字符串枚举值：text、image、audio、video，例如：text,image")
    output_modalities: str = Field(min_length=0, max_length=100, title="支持的输出模态", description="支持的输出模态，逗号分隔的字符串，字符串枚举值：text、image、audio、video，例如：text,image")
    model_version: str = Field(min_length=0, max_length=20, title="模型版本", description="模型版本，长度0-20")
    expire_date: datetime = Field(default=datetime(9999,12,30), title="模型过期时间", description="模型过期时间，默认为 9999-12-30")
    model_desc: str = Field(default="", title="模型描述", description="模型描述，json格式, 如果有, 至少包含字段 data")
    param_support_info: str = Field(default="", title="参数支持信息", description="参数支持信息，json格式, 包含支持的控制参数列表和每个参数的说明")
    token_len_info: str = Field(default="", title="token长度支持信息", description="token长度支持信息，json格式, 包含各模态输入输出的 token 长度限制")
    price_info: str = Field(default="", title="价格信息", description="价格信息,json格式, 包含计价货币、计价策略、计价单位、分层计价的层级定义等")
    reference_urls: str = Field(default="", title="相关链接", description="相关链接,json格式, 包括价格/参数支持/quota")
    note: str = Field(default="", title="备注", description="模型备注,json格式,如果有至少包含字段 data")
