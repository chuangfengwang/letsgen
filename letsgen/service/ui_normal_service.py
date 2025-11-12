# -*- coding: utf-8 -*-
"""
# @File    : ui_normal_service.py
# @Desc    :
# @Author  : chuangfeng.wang
# @Time    : 2025-11-02 20:29
"""
from __future__ import annotations

import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import config
import letsgen.db.pg_db_dao as pg_db_dao
import letsgen.exceptions.error_class as error_class
import letsgen.utils.password_util as password_util
from letsgen.db.pg_db_entity_auto import LetsgenUser, LetsgenBillAccount, LetsgenAccountApikey
from letsgen.entity.api_common_entity import BillAccountForm, ApiKeyForm, UserToAccountRoleEnum, WalletForm
from letsgen.entity.auth_entity import Identity
from letsgen.entity.ui_admin_router_entity import UserForm
from letsgen.entity.ui_normal_router_entity import LoginEntity
from letsgen.utils import codec_util

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
        identity = Identity(user_name=user_name, roles=role_list, account_name=None)
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

    async def create_account(self, account: BillAccountForm, identity: Identity) -> LetsgenBillAccount:
        """
        创建一个计费账号
        :param account: 用户填入的账号信息(bill account)
        :param identity: 创建者的用户信息(user)
        :return: 创建的账号
        """
        try:
            letsgen_account = await pg_db_dao.create_account(
                account, identity.user_name, config.default_currency_type_list)
            return letsgen_account
        except IntegrityError as e:
            msg = f"Conflict with existing data."
            logger.error(msg + f" account: {account.account_name}", exc_info=True)
            raise error_class.UiOpsConfigError(msg)
        except SQLAlchemyError as e:
            msg = f"Create account error. Please contact system admin."
            logger.error(msg + f" account: {account.account_name}", exc_info=True)
            raise error_class.UiOpsConfigError(msg)

    async def has_edit_role(self, account_name: str, user_name: str) -> bool:
        """检查 user_name 对 account_name 是否有修改权限"""
        role = await pg_db_dao.fetch_role(account_name, user_name)
        if role is None or role.role != UserToAccountRoleEnum.admin:
            return False
        return True

    async def create_apikey(self, apikey_form: ApiKeyForm, identity: Identity) -> LetsgenAccountApikey:
        """
        创建一个 apikey
        :param apikey_form:
        :param identity:
        :return:
        """
        # 检查 user 对 account_name 是否有所有权
        if not await self.has_edit_role(apikey_form.account_name, identity.user_name):
            msg = "Current user has no permission to create apikey for this bill account."
            logger.error(msg + f" user_name: {identity.user_name}, account_name: {apikey_form.account_name}")
            raise error_class.UiAuthorizationError(msg)
        # 创建 api-key
        apikey_value = "sk-" + codec_util.gen_uuid_base64()
        try:
            letsgen_account = await pg_db_dao.create_apikey(apikey_form, apikey_value)
            return letsgen_account
        except IntegrityError as e:
            msg = f"Conflict with existing data."
            logger.error(msg + f" apikey_name: {apikey_form.apikey_name}", exc_info=True)
            raise error_class.UiOpsConfigError(msg)
        except SQLAlchemyError as e:
            msg = f"Create apikey error. Please contact system admin."
            logger.error(msg + f" apikey_name: {apikey_form.apikey_name}", exc_info=True)
            raise error_class.UiOpsConfigError(msg)

    async def create_wallet(self, wallet_form: WalletForm, identity: Identity):
        """"创建钱包"""
        # 检查权限
        if not await self.has_edit_role(wallet_form.account_name, identity.user_name):
            msg = "Current user has no permission to create wallet for this bill account."
            logger.error(msg + f" user_name: {identity.user_name}, account_name: {wallet_form.account_name}")
            raise error_class.UiAuthorizationError(msg)
        # 创建钱包
        try:
            letsgen_account = await pg_db_dao.create_wallet(wallet_form)
            return letsgen_account
        except IntegrityError as e:
            msg = f"Conflict with existing data."
            logger.error(msg + f" currency_type: {wallet_form.currency_type}", exc_info=True)
            raise error_class.UiOpsConfigError(msg)
        except SQLAlchemyError as e:
            msg = f"Create apikey error. Please contact system admin."
            logger.error(msg + f" currency_type: {wallet_form.currency_type}", exc_info=True)
            raise error_class.UiOpsConfigError(msg)
