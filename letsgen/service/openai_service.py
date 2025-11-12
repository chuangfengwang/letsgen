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
from typing import Tuple, Any, Dict, Union, List, AsyncGenerator, cast, AsyncIterable

import httpx
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk, ChatCompletion

from letsgen.entity.llm_entity import LlmRequestContext
from letsgen.exceptions import error_class
from letsgen.service.llm_api_transfer import LlmTransferService
from letsgen.utils.function_util import all_param_expect_kwargs

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

    def pick_endpoint(self, model_id: str) -> Tuple[str, str]:
        """todo: 获取模型对应的 endpoint
        :return (provider, endpoint)"""
        provider, model = model_id.split("/", maxsplit=1)
        endpoint, _ = self.mock_provider.get(provider)
        return provider, endpoint

    def pick_endpoint_auth(self, endpoint: str) -> str:
        """todo: 获取 endpoint 对应的鉴权信息"""
        for _, v in self.mock_provider.items():
            if v[0] == endpoint:
                return v[1]
        return "place_holder_api_key"

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

    def transfer_param(self, body: dict, headers: dict, queries: dict) -> dict:
        """转换参数
        :return : 传给厂商的参数
        """
        param = {}
        extra_body = {}
        for key in body:
            if key in self._openai_chat_completions_param:
                # model 参数需要映射, 其他参数保持即可
                if key == "model":
                    param[key] = self.model_mapping(body[key])
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

    def fetch_price(self, model_id: str) -> dict:
        """获取模型的价格信息"""
        return {
            "prompt_tokens": 0.001,
            "completion_tokens": 0.002,
        }

    def update_cost(self, usage: dict) -> float:
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
