# -*- coding: utf-8 -*-
"""
# @File    : ui_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Body

import letsgen.dependencies.auth as auth
import letsgen.entity.ui_common_entity as ui_entity
import letsgen.service.ui_admin_service as ui_admin_service
import letsgen.service.ui_normal_service as ui_normal_service
from entity.auth_entity import Identity
from letsgen.entity.ui_admin_router_entity import FirstAdminUser, UserForm, EndpointForm, CredentialForm, \
    AddEndpointForModelForm

router = APIRouter(prefix="/api/ui/admin", tags=["ui-admin"])


@router.post("/create_first_admin_user")
async def create_first_admin_user(user: FirstAdminUser):
    """创建第一个 admin 用户"""
    await ui_admin_service.create_first_admin_user(user=user)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={}
    )


@router.post("/create_credential")
async def create_credential(
    credential_form: CredentialForm,
    identity: Identity = Depends(auth.admin_authorize_check),
):
    """创建 endpoint 凭证"""
    await ui_admin_service.create_credential(credential_form=credential_form, by_admin=identity)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={}
    )


@router.post("/query_valid_credential")
async def query_valid_credential(
    provider: str = Body(..., min_length=1, max_length=50, embed=True),
    identity: Identity = Depends(auth.admin_authorize_check),
):
    """查询有效 endpoint 凭证"""
    credential_list = await ui_admin_service.query_valid_credential(provider_name=provider)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={"credential_list": credential_list}
    )


# 修改 endpoint 凭证


@router.post("/create_endpoint")
async def create_endpoint(
    endpoint_form: EndpointForm,
    identity: Identity = Depends(auth.admin_authorize_check),
):
    """创建 endpoint"""
    await ui_admin_service.create_endpoint(endpoint_form=endpoint_form)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={}
    )


# 查询有效 endpoint
@router.post("/query_valid_endpoint")
async def query_valid_endpoint(
    provider: str | None = Body(None, min_length=1, max_length=50, embed=True),
    identity: Identity = Depends(auth.admin_authorize_check),
):
    """查询有效 endpoint"""
    endpoint_name_list = await ui_admin_service.query_valid_endpoint(provider_name=provider)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={"endpoint_list": endpoint_name_list}
    )


# 修改 endpoint

# 给模型添加 endpoint
@router.post("/add_endpoint_for_model")
async def add_endpoint_for_model(
    add_endpoint_for_model_form: AddEndpointForModelForm,
    identity: Identity = Depends(auth.admin_authorize_check),
):
    """给模型添加 endpoint"""
    await ui_admin_service.add_endpoint_for_model(form=add_endpoint_for_model_form)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={}
    )


# 添加模型
# 修改模型


# 创建其他用户
@router.post("/create_user")
async def create_user(
    user: UserForm,
    identity: Identity = Depends(auth.admin_authorize_check),
):
    """创建用户"""
    await ui_normal_service.create_user(user=user, by_admin=identity)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={}
    )

# 修改其他用户信息

# 为其他用户添加 llm 账户

# 修改其他用户 llm 账户
