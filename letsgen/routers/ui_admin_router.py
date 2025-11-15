# -*- coding: utf-8 -*-
"""
# @File    : ui_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""

from fastapi import APIRouter, Depends

import letsgen.dependencies.auth as auth
import letsgen.entity.ui_common_entity as ui_entity
import letsgen.service.ui_admin_service as ui_admin_service
import letsgen.service.ui_normal_service as ui_normal_service
from entity.auth_entity import Identity
from letsgen.entity.ui_admin_router_entity import FirstAdminUser, UserForm, EndpointForm, CredentialForm

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


# 创建 endpoint credential
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


# 添加 endpoint
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


# 修改 endpoint
# 添加 endpoint credential
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
