# -*- coding: utf-8 -*-
"""
# @File    : pg_db_dao.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 20:50
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import select, delete, update, insert, func, and_, or_, not_

import letsgen.db.pg_connection as pg_connection
from letsgen.db.pg_db_entity_auto import LetsgenUser, LetsgenBillAccount, LetsgenAccountApikey, \
    LetsgenUserAccountRlt, LetsgenWallet
from letsgen.entity.api_common_entity import BillAccountForm, ApiKeyForm, ApikeyStatusEnum, UiUserRoleEnum, \
    UserToAccountRoleEnum, WalletStatusEnum
from letsgen.entity.ui_admin_router_entity import UserForm
from letsgen.exceptions import error_class
from letsgen.utils.password_util import hash_password

logger = logging.getLogger(__name__)


async def admin_user_exist() -> bool:
    """检查是否存在管理员用户"""
    db_engine = await pg_connection.async_db_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM letsgen_user WHERE ui_role = 'admin'"))
        admin_count = result.fetchall()[0][0]
        return admin_count > 0


async def create_first_admin(user: LetsgenUser) -> LetsgenUser | None:
    """创建第一个管理员用户: 只在系统初始化时执行一次. 返回是否创建成功"""
    db_engine = await pg_connection.async_db_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        # 对密码进行哈希处理
        user.user_password = hash_password(user.user_password)
        # 创建管理员用户
        try:
            session.add(user)
            await session.commit()
            logger.info(f"Created first admin user success! user_name: {user.user_name}, id: {user.id}")
            await session.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Created first admin user failed! user_name: {user.user_name}", exc_info=True)
            return None


async def user_login(user_name: str) -> LetsgenUser | None:
    """用户登录查询"""
    db_engine = await pg_connection.async_db_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        stmt = select(LetsgenUser).where(LetsgenUser.user_name == user_name)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user


async def check_user_exist(user: UserForm) -> bool:
    """检查用户是否存在"""
    db_engine = await pg_connection.async_db_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        stmt_filtered = (
            select(func.count(1))
            .select_from(LetsgenUser)
            .where(LetsgenUser.user_name == user.user_name)
        )
        user_count = await session.scalar(stmt_filtered)
        if user_count > 0:
            raise error_class.UiParamConflictError(f"User name already exists: {user.user_name}")

        if user.user_email:
            stmt_filtered = (
                select(func.count(1))
                .select_from(LetsgenUser)
                .where(LetsgenUser.user_email == user.user_email)
            )
            user_count = await session.scalar(stmt_filtered)
            if user_count > 0:
                raise error_class.UiParamConflictError(f"User email already exists: {user.user_email}")

        if user.user_phone:
            stmt_filtered = (
                select(func.count(1))
                .select_from(LetsgenUser)
                .where(LetsgenUser.user_phone == user.user_phone)
            )
            user_count = await session.scalar(stmt_filtered)
            if user_count > 0:
                raise error_class.UiParamConflictError(f"User phone already exists: {user.user_phone}")
    return True


async def create_user(user: UserForm) -> LetsgenUser:
    """创建用户"""
    letsgen_user = LetsgenUser(
        user_name=user.user_name,
        user_email=user.user_email,
        user_password=hash_password(user.password_plain),
        user_phone=user.user_phone,
        ui_role=user.ui_role,
        user_status=user.user_status,
        note=user.note,
        **{}
    )
    db_engine = await pg_connection.async_db_pg_engine()
    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        async with session.begin():
            session.add(letsgen_user)
            await session.flush()
            return letsgen_user


async def create_account(
    account: BillAccountForm,
    by_user_name: str,
    default_currency_type_list: List[str]
) -> LetsgenBillAccount:
    """创建计费账号"""
    letsgen_account = LetsgenBillAccount(
        account_name=account.account_name,
        account_status=account.account_status,
        create_user_name=by_user_name,
        note=account.note if account.note else "",
        **{}
    )
    rlt = LetsgenUserAccountRlt(
        user_name=by_user_name,
        account_name=account.account_name,
        role=UserToAccountRoleEnum.admin,
        **{}
    )
    wallets = [
        LetsgenWallet(
            account_name=account.account_name,
            currency_type=currency,
            cur_balance=Decimal("0"),
            summary_charge=Decimal("0"),
            wallet_status=WalletStatusEnum.ok,
            note="",
            **{}
        ) for currency in default_currency_type_list
    ]
    db_engine = await pg_connection.async_db_pg_engine()
    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        async with session.begin():
            session.add(letsgen_account)
            session.add(rlt)
            if wallets:
                session.add_all(wallets)
            await session.flush()
            return letsgen_account


async def create_apikey(apikey: ApiKeyForm, apikey_value: str) -> LetsgenAccountApikey:
    """创建 api-key"""
    letsgen_apikey = LetsgenAccountApikey(
        account_name=apikey.account_name,
        apikey_name=apikey.apikey_name,
        apikey_value=apikey_value,
        apikey_status=ApikeyStatusEnum.ok,
        note=apikey.note if apikey.note else "",
        **{}
    )
    db_engine = await pg_connection.async_db_pg_engine()
    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        async with session.begin():
            session.add(letsgen_apikey)
            await session.flush()
            return letsgen_apikey


async def fetch_role(account_name: str, user_name: str) -> LetsgenUserAccountRlt | None:
    """检查 user_name 对 account_name 的权限"""
    db_engine = await pg_connection.async_db_pg_engine()
    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        stmt = select(LetsgenUserAccountRlt).where(
            and_(LetsgenUserAccountRlt.user_name == user_name,
                 LetsgenUserAccountRlt.account_name == account_name)
        )
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        return role


async def fetch_account_by_apikey(apikey_value: str) -> LetsgenAccountApikey | None:
    """通过 api-key 获取计费账户"""
    db_engine = await pg_connection.async_db_pg_engine()
    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        stmt = select(LetsgenAccountApikey).where(
            and_(LetsgenAccountApikey.apikey_value == apikey_value,
                 LetsgenAccountApikey.apikey_status == ApikeyStatusEnum.ok)
        )
        result = await session.execute(stmt)
        apikey = result.scalar_one_or_none()
        return apikey
