# -*- coding: utf-8 -*-
"""
# @File    : pg_log_dao.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-12 22:22
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import select, and_, or_, not_
from sqlalchemy.dialects.postgresql import insert

import letsgen.db.pg_connection as pg_connection
from letsgen.db.pg_log_entity_auto import LlmApiModelCallStat

logger = logging.getLogger(__name__)


async def fetch_model_call_stat(account_name: str) -> List[LlmApiModelCallStat]:
    """检查是否存在管理员用户"""
    db_engine = await pg_connection.async_log_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        stmt = select(LlmApiModelCallStat).where(LlmApiModelCallStat.account_name == account_name)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user


async def update_call_stat(delta_stat: LlmApiModelCallStat):
    stmt = insert(LlmApiModelCallStat).values(
        account_name=delta_stat.account_name,
        model_name=delta_stat.model_name,
        call_time_hour=delta_stat.call_time_hour,
        period_last_call_at=delta_stat.period_last_call_at,
        call_num=delta_stat.call_num,
        failed_call_num=delta_stat.failed_call_num,
        input_token_num=delta_stat.input_token_num,
        cached_token_num=delta_stat.cached_token_num,
        output_token_num=delta_stat.output_token_num,
        reason_token_num=delta_stat.reason_token_num,
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=["account_name", "model_name", "call_time_hour"],  # 唯一约束字段
        set_={
            "period_last_call_at": stmt.excluded.period_last_call_at,
            "call_num": LlmApiModelCallStat.call_num + stmt.excluded.call_num,
            "failed_call_num": LlmApiModelCallStat.failed_call_num + stmt.excluded.failed_call_num,
            "input_token_num": LlmApiModelCallStat.input_token_num + stmt.excluded.input_token_num,
            "cached_token_num": LlmApiModelCallStat.cached_token_num + stmt.excluded.cached_token_num,
            "output_token_num": LlmApiModelCallStat.output_token_num + stmt.excluded.output_token_num,
            "reason_token_num": LlmApiModelCallStat.reason_token_num + stmt.excluded.reason_token_num,
        }
    )
    db_engine = await pg_connection.async_log_pg_engine()

    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        await session.execute(stmt)
        await session.commit()
