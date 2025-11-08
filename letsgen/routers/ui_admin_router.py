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
from letsgen.entity.ui_admin_router_entity import FirstAdminUser, UserForm
from letsgen.service.ui_admin_service import UiAdminService
from letsgen.service.ui_normal_service import UiNormalService

router = APIRouter(prefix="/api/ui/admin")

ui_admin_service = UiAdminService()
ui_normal_service = UiNormalService()


@router.post("/create_first_admin_user")
async def create_first_admin_user(user: FirstAdminUser):
    """创建第一个 admin 用户"""
    await ui_admin_service.create_first_admin_user(user=user)
    return ui_entity.UiBaseResponse(
        status=0,
        message="",
        data={}
    )


# 添加/修改 endpoint
# 添加 endpoint credential
# 添加模型
# 修改模型


# 创建其他用户
@router.post("/create_user")
async def create_user(
    user: UserForm,
    identity: auth.Identity = Depends(auth.jwt_authorize_check),
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
