# -*- coding: utf-8 -*-
"""
# @File    : ui_normal_service.py
# @Desc    :
# @Author  : chuangfeng.wang
# @Time    : 2025-11-02 20:29
"""
from __future__ import annotations

import logging

import letsgen.db.pg_db_dao as pg_db_dao
import letsgen.exceptions.error_class as error_class
import letsgen.utils.password_util as password_util
from letsgen.db.pg_db_entity_auto import LetsgenUser
from letsgen.entity.auth_entity import Identity
from letsgen.entity.ui_admin_router_entity import UserForm
from letsgen.entity.ui_normal_router_entity import (LoginEntity, )

logger = logging.getLogger(__name__)


class UiNormalService:

    async def login(self, form: LoginEntity) -> str:
        """用户登录, 返回 jwt"""
        letgen_user = await pg_db_dao.user_login(form.user_name)
        if not letgen_user:
            msg = f"User not exist. user_name: {form.user_name}"
            logger.error(msg)
            raise error_class.UiAuthorizationError(msg)
        # 检查密码
        if not password_util.verify_password(form.password_plain, letgen_user.user_password):
            msg = f"User password incorrect."
            logger.error(msg + f" user_name: {form.user_name}")
            raise error_class.UiAuthorizationError(msg)
        # 生成 jwt
        jwt = password_util.create_jwt(letgen_user.user_name, [letgen_user.ui_role])
        logger.info(f"User ui login success. user_name: {form.user_name}")
        return jwt

    def check_jwt(self, jwt: str) -> Identity:
        """检查 jwt 有效性，返回 payload"""
        payload = password_util.verify_jwt(jwt)
        if not payload:
            msg = "Invalid JWT token. Please login again."
            logger.error(msg + f" jwt: {jwt}")
            raise error_class.UiAuthorizationError(msg)
        user_name = payload.get("user_name")
        role_list = payload.get("role")
        identity = Identity(user_name=user_name, roles=role_list)
        return identity

    async def create_user(self, user: UserForm, by_admin: Identity | None = None) -> LetsgenUser:
        """
        由 admin 创建一个用户
        :param user:
        :param by_admin:
        :return:
        """
        await pg_db_dao.check_user_exist(user)
        letsgen_user = await pg_db_dao.create_user(user)
        return letsgen_user
