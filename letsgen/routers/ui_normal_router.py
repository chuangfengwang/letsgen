# -*- coding: utf-8 -*-
"""
# @File    : ui_router.py
# @Desc    : 普通用户相关接口
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""

from fastapi import APIRouter, Depends

import letsgen.entity.ui_common_entity as ui_entity
from letsgen.dependencies import auth
from letsgen.entity.api_common_entity import BillAccountForm, ApiKeyForm, WalletForm
from letsgen.entity.auth_entity import Identity
from letsgen.entity.ui_admin_router_entity import UserForm
from letsgen.entity.ui_normal_router_entity import *
from letsgen.exceptions import error_class
from letsgen.service.ui_normal_service import UiNormalService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ui/normal")

ui_normal_service = UiNormalService()


# 用户登录
@router.post("/login")
async def login(form: LoginEntity):
    """创建第一个 admin 用户"""
    jwt = await ui_normal_service.login(form=form)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={"jwt": jwt}
    )


# 用户注册

# 修改密码

# 修改用户信息

# 获取用户信息


@router.post("/create_account")
async def create_account(
    account: BillAccountForm,
    identity: Identity = Depends(auth.jwt_authorize_check),
):
    """创建 llm 账户"""
    if not identity.user_name:
        msg = "Create account need ui login!"
        logger.error(msg)
        raise error_class.UiOpsConfigError(msg)
    await ui_normal_service.create_account(account, identity)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={}
    )


# 修改 llm 账户信息

# 删除 llm 账户

# 列出 llm 账户信息


# 创建 api-key
@router.post("/create_api_key")
async def create_api_key(
    apikey: ApiKeyForm,
    identity: Identity = Depends(auth.jwt_authorize_check),
):
    if not identity.user_name:
        msg = "Create ApiKey need ui login!"
        logger.error(msg)
        raise error_class.UiOpsConfigError(msg)
    letsgen_apikey = await ui_normal_service.create_apikey(apikey, identity)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={**letsgen_apikey.model_dump()}
    )
# 修改 api-key(名称,描述,状态)
# 删除 api-key
# 列出 api-key 信息

# 创建钱包
@router.post("/create_wallet")
async def create_wallet(
    wallet_form: WalletForm,
    identity: Identity = Depends(auth.jwt_authorize_check),
):
    if not identity.user_name:
        msg = "Create ApiKey need ui login!"
        logger.error(msg)
        raise error_class.UiOpsConfigError(msg)
    letsgen_apikey = await ui_normal_service.create_wallet(wallet_form, identity)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={**letsgen_apikey.model_dump()}
    )
# 修改钱包基本信息
