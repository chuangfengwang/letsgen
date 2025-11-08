# -*- coding: utf-8 -*-
"""
# @File    : ui_admin_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-01 22:45
"""
import logging

import letsgen.db.pg_db_dao as pg_db_dao
import letsgen.exceptions.error_class as error_class
from letsgen.db.pg_db_entity_auto import (LetsgenUser, )
from letsgen.entity.ui_admin_router_entity import FirstAdminUser

logger = logging.getLogger(__name__)


class UiAdminService:
    """Ui 管理员服务类"""

    async def create_first_admin_user(self, user: FirstAdminUser) -> bool:
        """创建第一个管理员用户

        Args:
            user (FirstAdminUser): 用户表单填写的基本信息

        Returns:
            bool: 创建成功返回 True，失败返回 False
        """
        if await pg_db_dao.admin_user_exist():
            msg = "First admin existing. Using admin user to create or confirm other admin users."
            logger.error(msg)
            raise error_class.UiOpsConfigError(msg)

        letsgen_user = LetsgenUser(
            user_name=user.user_name,
            user_password=user.password_plain,
            user_email=user.user_email,
            user_phone=user.user_phone,
            ui_role="admin",
            user_status="ok",
            **{}
        )
        letsgen_user = await pg_db_dao.create_first_admin(letsgen_user)
        if not letsgen_user:
            msg = f"Create first admin user failed. user_name: {user.user_name}"
            raise error_class.UiOpsConfigError(msg)
        # 创建成功
        return True
