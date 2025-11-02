# -*- coding: utf-8 -*-
"""
# @File    : ui_router.py
# @Desc    : 普通用户相关接口
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""

from fastapi import APIRouter

import letsgen.entity.ui_entity as ui_entity
from letsgen.entity.ui_normal_router_entity import *
from letsgen.service.ui_normal_service import UiNormalService

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


# 创建 llm 账户

# 修改 llm 账户信息

# 删除 llm 账户

# 列出 llm 账户信息


# 创建 api-key
# 删除 api-key
# 列出 api-key 信息
