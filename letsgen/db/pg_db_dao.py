# -*- coding: utf-8 -*-
"""
# @File    : pg_db_dao.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 20:50
"""
from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import select, delete, update, insert

import letsgen.db.pg_connection as pg_connection

from letsgen.db.pg_db_entity_auto import (LetsgenUser, )
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

# 创建用户
# 创建账号
# 创建 api-key
