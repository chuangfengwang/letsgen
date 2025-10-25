# -*- coding: utf-8 -*-
"""
# @File    : pg_db_dao.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 20:50
"""
import logging

import letsgen.db.pg_connection as pg_connection
import letsgen.exceptions.error_class as error_class
from letsgen.db.pg_db_entity import (User, )
from letsgen.utils.password_util import hash_password

logger = logging.getLogger(__name__)


async def create_first_admin(user: User) -> bool:
    """创建第一个管理员用户: 只在系统初始化时执行一次. 返回是否创建成功"""
    db_pool = await pg_connection.async_db_pg_pool()
    async with db_pool.acquire() as connection:
        # 检查管理员用户是否存在
        admin_count = await connection.fetchval(
            "SELECT COUNT(1) FROM letsgen_user WHERE ui_role = 'admin'"
        )
        if admin_count != 0:
            raise error_class.OpsUiConfigError(
                "first admin existing. Using admin user to create or confirm other users.")

        user.user_password = hash_password(user.user_password_plain)
        # 创建管理员用户
        try:
            await connection.execute(
                """
                INSERT INTO letsgen_user (user_name, user_email, user_password, user_phone, ui_role, user_status, note)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                user.user_name, user.user_email, user.user_password, user.user_phone, "admin", "ok", ""
            )
            logger.info(f"Created first admin user success! user_name: {user.user_name}")
            return True
        except Exception as e:
            logger.error(f"Created first admin user failed! user_name: {user.user_name}", exc_info=True)
            return False

# 创建用户
# 创建账号
# 创建 api-key
