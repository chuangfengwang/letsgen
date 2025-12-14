# -*- coding: utf-8 -*-
"""
# @File    : llm_api_transfer.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-14 16:15
"""
from __future__ import annotations

from typing import Tuple, Any, AsyncIterable

from letsgen.entity.llm_entity import LlmRequestContext
from letsgen.exceptions import error_class


class LlmTransferService:
    """LLM API 转换服务基类"""

    async def async_init(self):
        """异步初始化"""
        pass

    async def pick_endpoint(self, model_name: str) -> Tuple[str, str, str, str]:
        """获取模型对应的 endpoint
        :return (provider, endpoint_baseurl, auth, provider_model_id)"""
        raise NotImplementedError()

    def pick_proxy(self, endpoint: str) -> str | None:
        """获取 endpoint 对应的代理信息"""
        raise NotImplementedError()

    def transfer_param(self, body: dict, headers: dict, queries: dict, context: LlmRequestContext) -> dict:
        """转换参数
        :return : 传给厂商的参数
        """
        raise NotImplementedError()

    async def call_endpoint(self, endpoint: str, auth: str, params: dict, proxy: str | None) -> Any:
        """调用 endpoint"""
        raise NotImplementedError()

    def transfer_single_response(self, response: Any, context: LlmRequestContext) -> Any:
        """对非流式响应 转换返回结果"""
        raise NotImplementedError()

    async def transfer_stream_response(self, chunk: Any, context: LlmRequestContext) -> Any:
        """对流式响应 chunk 转换返回结果"""
        raise NotImplementedError()

    async def fetch_price(self, model_id: str) -> dict:
        """获取模型的价格信息"""
        raise NotImplementedError()

    async def update_cost(self, context: LlmRequestContext) -> float:
        """更新本次调用的费用"""
        raise NotImplementedError()

    def parse_model_and_stream(self, body: dict) -> Tuple[str, bool]:
        """解析 body 中的 model 和 stream 参数"""
        raise NotImplementedError()

    def stream_generator(self, stream_response, context: LlmRequestContext) -> AsyncIterable[str]:
        """流式响应生成器"""
        raise NotImplementedError()

    def parse_usage(self, context: LlmRequestContext) -> dict:
        """解析 usage"""
        raise NotImplementedError()

    async def db_stat_request(self, context: LlmRequestContext):
        """请求记录统计入库"""
        raise NotImplementedError()

    async def db_log_request_content(self, context: LlmRequestContext):
        """请求内容入库"""
        raise NotImplementedError()

    async def after_call_backend(self, context: LlmRequestContext):
        """接口调用完成后的后台任务"""
        model_id, is_stream = self.parse_model_and_stream(context.origin_body_param)
        # 计费
        usage = self.parse_usage(context)
        context.usage = usage
        context.price = await self.fetch_price(model_id)
        context.request_cost = await self.update_cost(context)
        context.mark_event_dt("update_cost_end")
        # 用量统计
        await self.db_stat_request(context)
        context.mark_event_dt("db_stat_request_end")
        # 调用记录存档
        await self.db_log_request_content(context)
        context.mark_event_dt("db_log_request_content_end")

    async def run(self, context: LlmRequestContext):
        """执行调用流程"""
        # 解析基础参数
        context.mark_event_dt("api_transfer_start")
        body = context.origin_body_param
        headers = {}
        if body is None:
            raise error_class.LlmParamError("Missing body param")
        model_id, is_stream = self.parse_model_and_stream(body)
        context.model_id = model_id
        context.is_stream = is_stream
        # 解析 endpoint 信息
        context.mark_event_dt("pick_endpoint_start")
        provider_name, endpoint_baseurl, edp_auth, provider_model_id = await self.pick_endpoint(model_id)
        if endpoint_baseurl is None:
            raise error_class.AdminConfigError(f"Cannot find endpoint for model {model_id}")
        context.provider_name = provider_name
        context.provider_endpoint = endpoint_baseurl
        context.provider_model_id = provider_model_id
        if edp_auth is None:
            raise error_class.AdminConfigError(f"Cannot find provider auth for endpoint {endpoint_baseurl}")
        context.provider_auth_id = edp_auth
        context.mark_event_dt("pick_endpoint_end")
        # 解析代理
        context.mark_event_dt("pick_proxy_start")
        proxy = self.pick_proxy(endpoint_baseurl)
        context.mark_event_dt("pick_proxy_end")
        # 解析请求参数
        context.mark_event_dt("param_transfer_start")
        provider_params = self.transfer_param(body, headers, {}, context)
        context.provider_body_param = provider_params
        context.mark_event_dt("param_transfer_end")
        context.mark_event_dt("call_endpoint_start")
        response = await self.call_endpoint(endpoint_baseurl, auth=edp_auth, params=provider_params, proxy=proxy)
        context.provider_response = response
        context.mark_event_dt("call_endpoint_end")
        context.mark_event_dt("transfer_response_start")
        if not context.is_stream:
            end_response = self.transfer_single_response(response, context)
            context.end_response = end_response
        else:
            end_response = response
        context.mark_event_dt("transfer_response_end")
        context.mark_event_dt("api_transfer_end")
        return end_response
