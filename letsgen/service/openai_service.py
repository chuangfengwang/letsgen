# -*- coding: utf-8 -*-
"""
# @File    : openai_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-08 19:41
"""
from __future__ import annotations

import json
import logging
import os
import random
from datetime import datetime
from typing import Tuple, Any, Dict, Union, List, AsyncGenerator, cast, AsyncIterable

import httpx
from openai import AsyncOpenAI, AsyncStream
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionChunk, ChatCompletion

import letsgen.db.pg_log_dao as pg_log_dao
from letsgen.db.pg_log_entity_auto import LlmApiModelCallStat
from letsgen.entity.llm_entity import LlmRequestContext
from letsgen.exceptions import error_class
from letsgen.service.llm_api_transfer import LlmTransferService
from letsgen.utils.function_util import all_param_expect_kwargs
import letsgen.db.pg_db_dao as pg_db_dao
from utils import password_util

logger = logging.getLogger(__name__)


class OpenAiService(LlmTransferService):
    """OpenAI 服务类"""

    def __init__(self):
        self._client = {}
        self._openai_chat_completions_param = set(self._get_openai_chat_completion_params())

        self.mock_provider = {
            "ollama": ("http://127.0.0.1:11434/v1", "place_holder_api_key"),
            "aliyun": ("https://dashscope.aliyuncs.com/compatible-mode/v1", os.environ.get("ALIYUN_API_KEY")),
            "volcengine": ("https://ark.cn-beijing.volces.com/api/v3", os.environ.get("VOLCENGINE_API_KEY")),
            "zhipu": ("https://open.bigmodel.cn/api/paas/v4", os.environ.get("ZHIPU_API_KEY")),
        }
        with open("volc_model_mapping.json", "r") as f:
            self.mock_model_mapping = json.load(f)

    def _get_openai_chat_completion_params(self) -> List[str]:
        """获取 OpenAI Chat Completion 支持的参数列表"""
        client = AsyncOpenAI(base_url="localhost", api_key="test")
        params = all_param_expect_kwargs(client.chat.completions.create)
        if "extra_headers" in params:
            params.remove("extra_headers")
        if "extra_query" in params:
            params.remove("extra_query")
        if "extra_body" in params:
            params.remove("extra_body")
        if "kwargs" in params:
            params.remove("kwargs")
        del client
        return params

    async def pick_endpoint(self, model_id: str) -> Tuple[str, str, str, str]:
        """获取模型对应的 endpoint
        :return (provider, endpoint_baseurl, auth, provider_model_id)"""
        # todo: 1. 查询模型对应的 provider
        provider, model = model_id.split("/", maxsplit=1)
        # 查询所有有效 endpoint
        edp_rlt_list = await pg_db_dao.query_model_valid_endpoint_rlt(model_id)
        if not edp_rlt_list:
            msg = f"No valid endpoints found for model. model_name: {model_id}"
            logger.error(msg)
            raise error_class.AdminConfigError(msg)

        # todo: 2. 选择当前用量少的 endpoint
        edp_rlt = random.choice(edp_rlt_list)
        endpoint_name, provider_model_id = edp_rlt.endpoint_name, edp_rlt.provider_model_id

        # 3. 查询选择的 endpoint 的凭证
        letsgen_provider_endpoint = await pg_db_dao.query_endpoint(provider, endpoint_name)
        if letsgen_provider_endpoint is None or (
            not letsgen_provider_endpoint.credential_name1 and
            not letsgen_provider_endpoint.credential_name2):
            # 没有有效凭证
            msg = f"No valid credit found for endpoint. endpoint_name: {endpoint_name}"
            logger.error(msg)
            raise error_class.AdminConfigError(msg)
        # 查询 credential
        credits_name = letsgen_provider_endpoint.credential_name1 \
            if letsgen_provider_endpoint.credential_name1 \
            else letsgen_provider_endpoint.credential_name2
        credential = await pg_db_dao.query_endpoint_credit(letsgen_provider_endpoint.provider_name, credits_name)
        if not credential:
            msg = (f"No credit found for endpoint. provider_name: {letsgen_provider_endpoint.provider_name}, "
                   f"credits_name: {credits_name}")
            logger.error(msg)
            raise error_class.AdminConfigError(msg)

        # todo: 4. 根据凭证类型构造不同 auth
        auth = password_util.decrypt_aes_gcm(credential.credential_value)

        # endpoint, auth = self.mock_provider.get(provider)
        return provider, letsgen_provider_endpoint.endpoint_baseurl, auth, provider_model_id

    def pick_proxy(self, endpoint: str) -> str | None:
        """获取 endpoint 对应的代理信息"""
        return None

    def build_httpx_client(
        self,
        proxy: str | None = None
    ) -> httpx.AsyncClient:
        """构建 httpx client"""
        if proxy in self._client:
            return self._client[proxy]
        # 连接池配置配置
        max_keepalive_connections = 100
        max_connections = 200
        keepalive_expiry = 100
        # 超时配置
        connect_timeout = 5.0
        read_write_timeout = 600.

        limits = httpx.Limits(
            max_keepalive_connections=max_keepalive_connections,  # 增加keepalive连接数
            max_connections=max_connections,  # 增加总连接数
            keepalive_expiry=keepalive_expiry  # 连接保持时间
        )

        client_config: Dict[str, Any] = {
            'timeout': httpx.Timeout(read_write_timeout, connect=connect_timeout),
            'limits': limits,
            # 'http2': True,  # 暂时禁用HTTP/2, 避免依赖h2包
        }

        if proxy:
            client_config['proxy'] = proxy

        client: httpx.AsyncClient = httpx.AsyncClient(**client_config)
        self._client[proxy] = client
        return client

    def close_httpx_client(self, proxy: str | None = None):
        """关闭代理关联的 httpx client"""
        if proxy in self._client:
            self._client[proxy].close()
            del self._client[proxy]

    def model_mapping(self, letsgen_model_id: str) -> str:
        """todo: 模型映射: letsgen_model_id -> 厂商模型ID"""
        provider, model = letsgen_model_id.split("/", maxsplit=1)
        if provider == "volcengine":
            return self.mock_model_mapping.get(model)
        else:
            return model

    def transfer_param(self, body: dict, headers: dict, queries: dict, context: LlmRequestContext) -> dict:
        """转换参数
        :return : 传给厂商的参数
        """
        param = {}
        extra_body = {}
        for key in body:
            if key in self._openai_chat_completions_param:
                # model 参数需要映射, 其他参数保持即可
                if key == "model":
                    param[key] = context.provider_model_id
                else:
                    param[key] = body[key]
            else:
                extra_body[key] = body[key]
        if extra_body:
            param["extra_body"] = extra_body
        if headers:
            param["extra_headers"] = headers
        if queries:
            param["extra_query"] = queries
        if body.get("stream", False):
            # 强制添加 usage 参数
            if "stream_options" not in param:
                param["stream_options"] = {"include_usage": True}
            else:
                param["stream_options"].update({"include_usage": True})
        return param

    async def call_endpoint(
        self,
        endpoint: str,
        auth: str,
        params: dict,
        proxy: str | None = None
    ) -> Any:
        """调用 endpoint"""
        httpx_client = self.build_httpx_client(proxy=proxy)
        openai_client = AsyncOpenAI(base_url=endpoint, api_key=auth, http_client=httpx_client)
        response: Union[AsyncStream[ChatCompletionChunk], ChatCompletion] = \
            await openai_client.chat.completions.create(**params)
        return response

    def transfer_response(self, response: Any) -> Any:
        """转换返回结果"""
        return response

    async def fetch_price(self, model_id: str) -> dict:
        """获取模型的价格信息"""
        return {
            "prompt_tokens": 0.001,
            "completion_tokens": 0.002,
        }

    async def update_cost(self, usage: dict) -> float:
        """更新本次调用的费用"""
        return 0.

    def parse_model_and_stream(self, body: dict) -> Tuple[str, bool]:
        """解析 body 中的 model 和 stream 参数"""
        model_id = body.get("model")
        if model_id is None:
            raise error_class.LlmParamError("Missing model param")
        is_stream = body.get("stream", False)
        return model_id, is_stream

    def stream_generator(
        self,
        stream_response,
        context: LlmRequestContext
    ) -> AsyncIterable[str]:
        """同步转异步调用"""

        async def _wrapper(
            stream_response,
            context: LlmRequestContext
        ) -> AsyncGenerator[str, None]:
            """流式响应生成器"""
            try:
                stream_response = cast(AsyncStream[ChatCompletionChunk], stream_response)
                async for chunk in stream_response:
                    context.end_chunk = chunk
                    data = chunk.model_dump_json()
                    yield f"data: {data}\n\n"
            except Exception as e:
                context.error = e
                error_msg = e.message if hasattr(e, "message") else str(e)
                msg = {"error": error_msg, "letsgen_req_id": context.letsgen_req_id, "qtraceid": context.trace_id}
                logger.error(f"OpenAiService stream_generator error: {json.dumps(msg)}", exc_info=True)
                yield f"event: error\n"
                yield f"data: {json.dumps(msg)}\n\n"
            finally:
                yield "data: [DONE]\n\n"

        return _wrapper(
            stream_response,
            context
        )

    def parse_usage(self, context: LlmRequestContext) -> dict:
        """解析 usage"""
        if context.is_stream:
            end_chunk = cast(ChatCompletionChunk, context.end_chunk)
            usage = end_chunk.usage if hasattr(end_chunk, "usage") and end_chunk.usage is not None else {}
        else:
            response = cast(ChatCompletion, context.provider_response)
            usage = response.usage if hasattr(response, "usage") and response.usage is not None else {}
        return usage

    async def db_log_request(self, context: LlmRequestContext):
        """请求记录入库"""
        try:
            request_in_dt = context.get_event_dt("request_in")
            call_time_hour_format = "%Y-%m-%dT%H"
            call_time_hour = datetime.strptime(request_in_dt.strftime(call_time_hour_format), call_time_hour_format)
            # todo: 判断调用失败
            is_failed = context.error is not None
            usage = cast(CompletionUsage, context.usage)

            if usage:
                input_token_num = usage.prompt_tokens
                cached_token_num = 0
                output_token_num = usage.completion_tokens
                reason_token_num = 0
                if usage.prompt_tokens_details:
                    cached_token_num = usage.prompt_tokens_details.cached_tokens
                    if cached_token_num is None:
                        cached_token_num = 0
                if usage.completion_tokens_details:
                    reason_token_num = usage.completion_tokens_details.reasoning_tokens
                    if reason_token_num is None:
                        reason_token_num = 0
            else:
                input_token_num = 0
                cached_token_num = 0
                output_token_num = 0
                reason_token_num = 0

            delta_stat = LlmApiModelCallStat(
                account_name=context.identity.account_name,
                model_name=context.model_id,
                call_time_hour=call_time_hour,
                period_last_call_at=request_in_dt,
                call_num=1,
                failed_call_num=1 if is_failed else 0,
                input_token_num=input_token_num,
                cached_token_num=cached_token_num,
                output_token_num=output_token_num,
                reason_token_num=reason_token_num,
                **{}
            )
            await pg_log_dao.update_call_stat(delta_stat)
        except Exception as e:
            logger.error(f"OpenAiService db_log_request error. "
                         f"letsgen_req_id: {context.letsgen_req_id}, qtraceid: {context.trace_id}, "
                         f"context.usage: {context.usage}", exc_info=True)
