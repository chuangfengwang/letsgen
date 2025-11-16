# -*- coding: utf-8 -*-
"""
# @File    : openai_entity.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-08 19:42
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Dict, Any

from pydantic import BaseModel, ConfigDict

import letsgen.entity.auth_entity as auth_entity


class LlmRequestContext(BaseModel):
    # 请求唯一标识
    letsgen_req_id: str | None = None
    # trace_id 用于请求链路追踪
    trace_id: str | None = None
    # 项目代号, 用于按项目导出调用记录
    proj_id: str | None = None
    # 身份信息
    identity: auth_entity.Identity | None = None
    # 各阶段的时间戳
    stage_ts: List[Tuple[str, datetime]] = []
    # error 信息
    error: Any = None

    # 请求路径
    request_path: str | None = None
    # 请求方法
    request_method: str | None = None
    # 来源 ip
    client_ip: str | None = None

    # 原始 body 请求参数
    origin_body_param: Dict[str, Any] | None = None
    # 发给厂商的请求参数
    provider_body_param: Dict[str, Any] | None = None
    # letsgen 请求的模型名
    model_id: str | None = None
    # 是否流式
    is_stream: bool | None = None
    # 厂商代号
    provider_name: str | None = None
    # 厂商鉴权代号
    provider_auth_id: str | None = None
    # 厂商 endpoint
    provider_endpoint: str | None = None
    # 厂商侧模型代号
    provider_model_id: str | None = None
    # 厂商返回的原始结果
    provider_response: Any | None = None
    # 最终返回给用户的结果
    end_response: Any | None = None
    # 对于流式, 保存最后一个 chunk
    end_chunk: Any | None = None

    # 本次次调用 token 用量
    usage: Any | None = None
    # 价格信息
    price: Dict[str, Any] | None = None
    # 本次花费
    request_cost: float | None = None

    # model 配置信息
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    def mark_event_dt(self, event_name: str) -> datetime:
        """记录事件时间戳"""
        now = datetime.now()
        self.stage_ts.append((event_name, now))
        return now

    def get_event_dt(self, event_name: str) -> datetime | None:
        """获取事件时间戳"""
        for entry in self.stage_ts:
            if entry[0] == event_name:
                return entry[1]
        return None
