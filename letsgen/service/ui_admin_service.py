# -*- coding: utf-8 -*-
"""
# @File    : ui_admin_service.py
# @Desc    : Ui 管理员服务
# @Author  : chuangfeng.wang
# @Time    : 2025-11-01 22:45
"""
from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import letsgen.db.pg_db_dao as pg_db_dao
import letsgen.exceptions.error_class as error_class
import letsgen.utils.password_util as password_util
from letsgen.entity.auth_entity import Identity
from letsgen.db.pg_db_entity_auto import (LetsgenUser, LetsgenProviderCredential, LetsgenProviderEndpoint,
                                          LetsgenModelEndpointRlt, )
from letsgen.entity.ui_admin_router_entity import FirstAdminUser, CredentialForm, EndpointForm, AddEndpointForModelForm

logger = logging.getLogger(__name__)


async def create_first_admin_user(user: FirstAdminUser) -> bool:
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
    letsgen_user = await pg_db_dao.register_user(letsgen_user)
    if not letsgen_user:
        msg = f"Create first admin user failed. user_name: {user.user_name}"
        raise error_class.UiOpsConfigError(msg)
    # 创建成功
    return True


async def create_credential(
    credential_form: CredentialForm,
    by_admin: Identity
) -> LetsgenProviderCredential:
    """创建凭证"""
    # 加密凭证进行存储
    encrypt_credential = password_util.encrypt_aes_gcm(credential_form.credential_value)
    letsgen_credential = LetsgenProviderCredential(
        provider_name=credential_form.provider_name,
        credential_name=credential_form.credential_name,
        credential_type=credential_form.credential_type,
        credential_value=encrypt_credential,
        credential_status=credential_form.credential_status,
        create_user=by_admin.user_name,
        **{}
    )
    if credential_form.expire_at:
        letsgen_credential.expire_at = credential_form.expire_at
    try:
        letsgen_credential = await pg_db_dao.create_credential(letsgen_credential)
    except IntegrityError as e:
        msg = f"Conflict with existing data."
        logger.error(msg + f" provider_name: {credential_form.provider_name},"
                           f" credential_name: {credential_form.credential_name}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    except SQLAlchemyError as e:
        msg = f"Create credential error. Please contact system admin."
        logger.error(msg + f" provider_name: {credential_form.provider_name},"
                           f" credential_name: {credential_form.credential_name}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    if not letsgen_credential:
        msg = (f"Create credential failed. provider_name: {credential_form.provider_name}, "
               f"credential_name: {credential_form.credential_name}")
        raise error_class.UiOpsConfigError(msg)
    return letsgen_credential


async def query_valid_credential(provider_name: str) -> List[str]:
    """查询有效凭证"""
    valid_credential_list = await pg_db_dao.query_valid_credential(provider_name)
    return valid_credential_list


async def create_endpoint(endpoint_form: EndpointForm):
    # todo: check endpoint_proxies, endpoint_path_info, endpoint_quota
    # 检查 credential_name 是否有效
    valid_credential_list = await pg_db_dao.query_valid_credential(endpoint_form.provider_name)
    if not valid_credential_list:
        msg = f"Provider has no valid credential."
        logger.error(msg + f" provider_name: {endpoint_form.provider_name}", exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    if endpoint_form.credential_name1 and endpoint_form.credential_name1 not in valid_credential_list:
        msg = f"Credential1 has not register."
        logger.error(msg + f" provider_name: {endpoint_form.provider_name}, "
                           f"credential_name1: {endpoint_form.credential_name1}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    if endpoint_form.credential_name2 and endpoint_form.credential_name1 not in valid_credential_list:
        msg = f"Credential2 has not register."
        logger.error(msg + f" provider_name: {endpoint_form.provider_name}, "
                           f"credential_name2: {endpoint_form.credential_name2}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    # 创建有效 endpoint
    letsgen_provider_endpoint = LetsgenProviderEndpoint(
        provider_name=endpoint_form.provider_name,
        endpoint_name=endpoint_form.endpoint_name,
        credential_name1=endpoint_form.credential_name1,
        credential_name2=endpoint_form.credential_name2,
        endpoint_status=endpoint_form.endpoint_status,
        endpoint_baseurl=endpoint_form.endpoint_baseurl,
        endpoint_region=endpoint_form.endpoint_region,
        endpoint_proxies=endpoint_form.endpoint_proxies,
        api_format=endpoint_form.api_format,
        endpoint_path_info=endpoint_form.endpoint_path_info,
        endpoint_quota=endpoint_form.endpoint_quota,
        note=endpoint_form.note,
        **{}
    )

    try:
        letsgen_credential = await pg_db_dao.create_endpoint(letsgen_provider_endpoint)
        if not letsgen_credential:
            msg = (f"Create provider endpoint failed. provider_name: {endpoint_form.provider_name}, "
                   f"endpoint_name: {endpoint_form.endpoint_name}")
            logger.error(msg, exc_info=True)
            raise error_class.UiOpsConfigError(msg)
        return letsgen_credential
    except IntegrityError as e:
        msg = f"Conflict with existing data."
        logger.error(msg + f" provider_name: {endpoint_form.provider_name},"
                           f" endpoint_name: {endpoint_form.endpoint_name}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    except SQLAlchemyError as e:
        msg = f"Create provider endpoint error. Please contact system admin."
        logger.error(msg + f" provider_name: {endpoint_form.provider_name},"
                           f" endpoint_name: {endpoint_form.endpoint_name}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)


async def query_valid_endpoint(provider_name: str | None) -> List[str]:
    """查询有效 endpoint"""
    valid_endpoint_list = await pg_db_dao.query_provider_valid_endpoint(provider_name)
    endpoint_name_list = [endpoint.endpoint_name for endpoint in valid_endpoint_list]
    return endpoint_name_list


async def add_endpoint_for_model(form: AddEndpointForModelForm):
    """为模型添加 endpoint"""
    # 检查 endpoint 有效性
    valid_endpoint_name_list = await query_valid_endpoint(form.provider_name)
    if form.endpoint_name not in valid_endpoint_name_list:
        msg = (f"Add model endpoint failed.  provider: {form.endpoint_name} "
               f"has no endpoint_name: {form.endpoint_name}")
        "model: {form.model_name},"
        logger.error(msg + f" model: {form.model_name}", exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    # 为模型添加 endpoint
    letsgen_model_endpoint_rlt = LetsgenModelEndpointRlt(
        model_name=form.model_name,
        provider_name=form.provider_name,
        endpoint_name=form.endpoint_name,
        provider_model_id=form.provider_model_id,
        m_edp_status=form.m_edp_status,
        note=form.note,
        **{}
    )
    if form.provider_params is not None:
        letsgen_model_endpoint_rlt.provider_params = form.provider_params
    if form.rpd_limit is not None:
        letsgen_model_endpoint_rlt.rpd_limit = form.rpd_limit
    if form.rpd_duration is not None:
        letsgen_model_endpoint_rlt.rpd_duration = form.rpd_duration
    if form.tpd_limit is not None:
        letsgen_model_endpoint_rlt.tpd_limit = form.tpd_limit
    if form.tpd_duration is not None:
        letsgen_model_endpoint_rlt.tpd_duration = form.tpd_duration
    if form.ifr_limit is not None:
        letsgen_model_endpoint_rlt.ifr_limit = form.ifr_limit

    try:
        letsgen_model_endpoint_rlt = await pg_db_dao.add_endpoint_for_model(letsgen_model_endpoint_rlt)
        if not letsgen_model_endpoint_rlt:
            msg = (f"Add model endpoint failed. model_name: {form.model_name}, provider_name: {form.provider_name}, "
                   f"endpoint_name: {form.endpoint_name}")
            logger.error(msg, exc_info=True)
            raise error_class.UiOpsConfigError(msg)
        return letsgen_model_endpoint_rlt
    except IntegrityError as e:
        msg = f"Conflict with existing data."
        logger.error(msg + f" model_name: {form.model_name},"
                           f" provider_name: {form.provider_name},"
                           f" endpoint_name: {form.endpoint_name}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)
    except SQLAlchemyError as e:
        msg = f"Add model endpoint error. Please contact system admin."
        logger.error(msg + f" model_name: {form.model_name},"
                           f" provider_name: {form.provider_name},"
                           f" endpoint_name: {form.endpoint_name}",
                     exc_info=True)
        raise error_class.UiOpsConfigError(msg)
