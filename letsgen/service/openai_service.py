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
from openai.types.chat.chat_completion import Choice
from pydantic import TypeAdapter

import letsgen.config as config
import letsgen.db.pg_db_dao as pg_db_dao
import letsgen.db.pg_log_dao as pg_log_dao
from letsgen.db.pg_log_entity_auto import LlmApiModelCallStat, LlmApiRequestMetaLog, LlmApiRequestBodyLog
from letsgen.entity.llm_entity import LlmRequestContext
from letsgen.exceptions import error_class
from letsgen.service.llm_api_transfer import LlmTransferService
from letsgen.service.log_content_service import LogContentService
from letsgen.service.price_service import calculate_fee
from letsgen.system.global_service import log_content_service
from letsgen.utils import password_util
from letsgen.utils.function_util import all_param_expect_kwargs

logger = logging.getLogger(__name__)


# openai chat completions 接口
class OpenAiChatCompletionsService(LlmTransferService):
    """OpenAI chat completions 服务类"""

    def __init__(self):
        self._client = {}
        self._openai_chat_completions_param = set(self._get_openai_chat_completion_params())

        self.mock_provider = {
            "ollama": ("http://127.0.0.1:11434/v1", "place_holder_api_key"),
            "aliyun": ("https://dashscope.aliyuncs.com/compatible-mode/v1", os.environ.get("ALIYUN_API_KEY")),
            "volcengine": ("https://ark.cn-beijing.volces.com/api/v3", os.environ.get("VOLCENGINE_API_KEY")),
            "zhipu": ("https://open.bigmodel.cn/api/paas/v4", os.environ.get("ZHIPU_API_KEY")),
        }
        with open(os.path.join(config.cur_dir, "volc_model_mapping.json"), "r") as f:
            self.mock_model_mapping = json.load(f)

        self.log_content_service: LogContentService = log_content_service

    async def async_init(self):
        """异步初始化"""
        pass

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

    def transfer_single_response(self, response: Any, context: LlmRequestContext) -> Any:
        """对非流式: 转换返回结果"""
        if context.provider_name == "google":
            # google 的 completion_tokens 不包含 reasoning token, 需要用 total_tokens - prompt_tokens 来计算
            response: ChatCompletion = cast(ChatCompletion, response)
            usage = response.usage
            # 对齐其他厂商的统计口径
            usage.completion_tokens = usage.total_tokens - usage.prompt_tokens
        return response

    async def transfer_stream_response(self, chunk: str, context: LlmRequestContext) -> Any:
        """对流式响应, 利用流式回调累积结果. todo: 重构"""
        # 只留下有效 chunk 信息
        if chunk.startswith("data: "):
            chunk = chunk[len("data: "):]

        if chunk.startswith("[DONE]"):
            # 删除占位字段
            if context.end_response is not None:
                if "choices" in context.end_response and len(context.end_response["choices"]) > 0 \
                    and "message" in context.end_response["choices"][0] \
                    and "building_tool_calls" in context.end_response["choices"][0]["message"]:
                    del context.end_response["choices"][0]["message"]["building_tool_calls"]
            return

        chunk_json = json.loads(chunk)
        if context.end_response is None:
            context.end_response = {
                "id": "",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "reasoning_content": "",
                        "tool_calls": [],  # 存储 ChatCompletionMessageToolCall 列表
                        # 用于临时存储正在构建中的 tool_calls（按 index 索引）
                        # Key: tool_call id(str), Value: ChatCompletionMessageToolCall object
                        "building_tool_calls": {}
                    }
                }],
                "created": 0,
                "model": "",
                "object": "chat.completion",
                "system_fingerprint": "",
                "usage": None,  # usage 信息通常只在流结束时出现
            }
        end_response = context.end_response
        # 初始化用于累加消息内容的结构
        accumulated_message: Dict[str, Any] = end_response["choices"][0]
        building_tool_calls: Dict[str, Any] = \
            cast(Dict[str, Any],
                 cast(object, accumulated_message.get("message", {})["building_tool_calls"]))
        # 1. 处理顶级元数据 (id, model, created, system_fingerprint)
        if chunk_json.get("id"):
            end_response["id"] = chunk_json.get("id")
        if chunk_json.get("model"):
            end_response["model"] = chunk_json.get("model")
        if chunk_json.get("created"):
            end_response["created"] = chunk_json.get("created")
        if chunk_json.get("system_fingerprint"):
            end_response["system_fingerprint"] = chunk_json.get("system_fingerprint")
        if chunk_json.get("service_tier"):
            end_response["service_tier"] = chunk_json.get("service_tier")

        # 其他没有特殊处理的 key 原样复制, 且只保留最后一次出现的值
        for key, value in chunk_json.items():
            if key in ("choices", "usage", "id", "model", "created", "object", "system_fingerprint", "service_tier"):
                continue
            end_response[key] = value

        # 2. 遍历 choices 并累加内容 (通常只有一个 choice)
        if "choices" in chunk_json and len(chunk_json.get("choices", [])) > 0:
            choice = chunk_json.get("choices")[0]
            delta = choice.get("delta")

            # 累加文本内容
            if delta.get("content"):
                accumulated_message["message"]["content"] += delta.get("content")
            if delta.get("reasoning_content"):
                accumulated_message["message"]["reasoning_content"] += delta.get("reasoning_content")
            if delta.get("reasoning"):
                accumulated_message["message"]["reasoning_content"] += delta.get("reasoning")
            # 累加工具调用
            if delta.get("tool_calls", []):
                for tool_call_chunk in delta.get("tool_calls"):
                    idx = tool_call_chunk.get("id")

                    # 初始化或获取当前 tool_call
                    if idx not in building_tool_calls:
                        building_tool_calls[idx] = {
                            "id": idx,
                            "type": "function",
                            "function": {
                                "name": "",
                                "arguments": ""
                            }
                        }

                    # 合并 tool_call id
                    if tool_call_chunk.get("id"):
                        building_tool_calls[idx]["id"] = tool_call_chunk.get("id")

                    # 合并 function name
                    if tool_call_chunk.get("function") and tool_call_chunk.get("function", {}).get("name"):
                        building_tool_calls[idx]["function"]["name"] = tool_call_chunk.get("function").get("name")

                    # 合并 function arguments
                    if tool_call_chunk.get("function") and tool_call_chunk.get("function", {}).get("arguments"):
                        building_tool_calls[idx]["function"]["arguments"] += tool_call_chunk.get("function").get(
                            "arguments")

                    # 其他额外信息直接复制. 例如: google 的 extra_content
                    for key, value in tool_call_chunk.items():
                        if key in ("id", "function", "arguments"):
                            continue
                        building_tool_calls[idx][key] = value

            # 3. 处理结束信息 (finish_reason 和 usage)
            if choice.get("finish_reason"):
                # 累加完所有 tool_calls 后，将其转换为最终对象结构
                accumulated_message["message"]["tool_calls"] = [
                    tc for tc in building_tool_calls.values()
                ]
                accumulated_message["finish_reason"] = choice.get("finish_reason")
            # 其他额外信息, 原样复制
            for key, value in choice.items():
                if key in ("content", "tool_calls", "finish_reason", "delta"):
                    continue
                accumulated_message[key] = value

        # 4. 累加 usage 信息 (通常在最后一个 chunk 中)
        if chunk_json.get("usage", {}):
            usage = chunk_json.get("usage")
            if context.provider_name == "google":
                # google 的 completion_tokens 不包含 reasoning token, 需要用 total_tokens - prompt_tokens 来计算
                # 对齐其他厂商的统计口径
                usage["completion_tokens"] = usage["total_tokens"] - usage["prompt_tokens"]
            end_response["usage"] = usage

        # 5. 把累积的消息更新到 ["choices"][0] 里
        end_response["choices"][0] = accumulated_message
        # 6. 把当前 chunk 记作最后一个 chunk
        context.end_chunk = chunk_json

    async def fetch_price(self, model_id: str) -> Tuple[dict, str]:
        """获取模型的价格信息
        :return (dict, str) 其中 dict 是各类token的计费单价, str 是计费方式
        """
        price = {
            "currency": "USD",  # 计价货币单位
            "strategy": "input-tiered",  # 计价策略, 当前仅支持 input-tiered, 即根据输入长度分层计价
            "unit": "1M-token",  # 计价单位, 通常是 1M-token, 表示每百万token
            "tiers": [  # 分层计价的层级定义
                {
                    "range": "[0,200k]",  # 输入长度范围. k:1024, m:1024*1024
                    "input_text": 2.0,  # 输入文本 token 的价格
                    "input_image": 2.0,  # 输入图像 token 的价格
                    "input_video": 2.0,  # 输入视频 token 的价格
                    "input_audio": 2.0,  # 输入音频 token 的价格
                    "output_text": 12.0,  # 输出文本 token 的价格
                    "output_image": 120.0,  # 输出图像 token 的价格
                    "cached": {
                        "strategy": "ttl",  # 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
                        "ttl": [
                            {
                                "range": "(0,5m]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                                "read_text": 0.5,  # 读取文本缓存 token 的价格
                                "read_image": 0.5,  # 读取图像缓存 token 的价格
                                "read_video": None,  # 不支持这种输入
                                "read_audio": None,  # 不支持这种输入
                                "write_text": 6.25,  # 写入文本缓存 token 的价格
                                "write_image": 6.25,  # 写入图像缓存 token 的价格
                                "write_video": None,  # 不支持这种输入
                                "write_audio": None,  # 不支持这种输入
                            },
                            {
                                "range": "(5m,1h]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                                "read_text": 0.5,  # 读取文本缓存 token 的价格
                                "read_image": 0.5,  # 读取图像缓存 token 的价格
                                "read_video": None,  # 不支持这种输入
                                "read_audio": None,  # 不支持这种输入
                                "write_text": 10,  # 写入文本缓存 token 的价格
                                "write_image": 10,  # 写入图像缓存 token 的价格
                                "write_video": None,  # 不支持这种输入
                                "write_audio": None,  # 不支持这种输入
                            }
                        ]
                    }
                },
                {
                    "range": "(200k,inf)",  # 输入长度范围, inf 表示无穷大, 无所谓开闭区间
                    "input_text": 4.0,  # 输入文本 token 的价格
                    "input_image": 4.0,  # 输入图像 token 的价格
                    "input_video": 4.0,  # 输入视频 token 的价格
                    "input_audio": 4.0,  # 输入音频 token 的价格
                    "output_text": 18.0,  # 输出文本 token 的价格
                    "output_image": None,  # 不存在这种情况
                    "cached": {
                        "strategy": "ttl",  # 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
                        "ttl": [
                            {
                                "range": "(0,5m]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                                "read_text": 0.5,  # 读取文本缓存 token 的价格
                                "read_image": 0.5,  # 读取图像缓存 token 的价格
                                "read_video": None,  # 不支持这种输入
                                "read_audio": None,  # 不支持这种输入
                                "write_text": 6.25,  # 写入文本缓存 token 的价格
                                "write_image": 6.25,  # 写入图像缓存 token 的价格
                                "write_video": None,  # 不支持这种输入
                                "write_audio": None,  # 不支持这种输入
                            },
                            {
                                "range": "(5m,1h]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                                "read_text": 0.5,  # 读取文本缓存 token 的价格
                                "read_image": 0.5,  # 读取图像缓存 token 的价格
                                "read_video": None,  # 不支持这种输入
                                "read_audio": None,  # 不支持这种输入
                                "write_text": 10,  # 写入文本缓存 token 的价格
                                "write_image": 10,  # 写入图像缓存 token 的价格
                                "write_video": None,  # 不支持这种输入
                                "write_audio": None,  # 不支持这种输入
                            }
                        ]
                    }
                }
            ]
        }
        pay_strategy = "input-tiered"  # 根据输入token长度分层计价
        return price, pay_strategy

    async def update_cost(self, context: LlmRequestContext) -> Tuple[float, str]:
        """更新本次调用的费用"""
        pay_strategy = context.pay_strategy
        usage: dict = context.usage
        price: dict = context.price
        if pay_strategy == "input-tiered":
            # 按输入 token 长度阶梯计价
            cost, currency = calculate_fee(usage, price, cached_ttl=None)
            # todo: 更新钱包余额

            return cost, currency
        else:
            model_id = context.model_id
            msg = f"Unsupported pay_strategy type. pay_strategy: {pay_strategy}, model_id: {model_id}"
            logger.error(msg)
            raise error_class.AdminConfigError(msg)

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
            end_chunk = cast(dict, context.end_chunk)
            usage = end_chunk['usage'] if end_chunk.get("usage", {}) else {}
            return usage
        else:
            response = cast(ChatCompletion, context.provider_response)
            usage = response.usage if hasattr(response, "usage") and response.usage is not None else {}
            return usage.model_dump()

    async def db_stat_request(self, context: LlmRequestContext):
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
                model_id=context.model_id,
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

    async def db_log_request_content(self, context: LlmRequestContext):
        """请求内容入库"""
        try:
            if not config.enable_request_response_log:
                return
            # 记录元数据  ####################################################

            # 请求参数
            log_time = datetime.now()
            account_name = context.identity.account_name
            model_id = context.model_id
            gen_api_path = context.request_path
            gen_req_id = context.letsgen_req_id
            gen_trace_id = context.trace_id if context.trace_id else ""
            interact_mode = "stream" if context.is_stream else "single"
            provider_name = context.provider_name
            provider_region = context.provider_region if context.provider_region else ""

            origin_param = context.origin_body_param
            messages = origin_param.get("messages")
            tools = origin_param.get("tools", [])
            if messages is not None:
                del origin_param["messages"]
            if tools:
                del origin_param["tools"]
            request_body_meta = origin_param

            # 几个时间
            request_in_time = context.get_event_dt("request_in")
            provider_in_time = context.get_event_dt("response_out_start")
            first_token_time = context.get_event_dt("response_chunk_start")
            provider_end_time = context.get_event_dt("response_chunk_end")
            response_out_time = context.get_event_dt("response_out_end")

            # 响应元数据
            end_response = context.end_response
            if context.is_stream:
                # todo: 解析流式响应
                provider_response = ChatCompletion.model_validate(end_response)
                provider_req_id = provider_response.id
            else:
                provider_response: ChatCompletion = cast(ChatCompletion, context.provider_response)
                provider_req_id = provider_response.id

            adapter = TypeAdapter(List[Choice])
            choices = adapter.dump_python(provider_response.choices)
            reply_body_meta = provider_response.model_dump()
            del reply_body_meta["choices"]

            meta_log: LlmApiRequestMetaLog = LlmApiRequestMetaLog(
                log_time=log_time,
                account_name=account_name,
                model_id=model_id,
                gen_api_path=gen_api_path,
                gen_req_id=gen_req_id,
                gen_trace_id=gen_trace_id,
                interact_mode=interact_mode,
                provider_name=provider_name,
                provider_region=provider_region,
                provider_req_id=provider_req_id,
                request_body_meta=json.dumps(request_body_meta, ensure_ascii=False),
                reply_body_meta=json.dumps(reply_body_meta, ensure_ascii=False),
                request_in_time=request_in_time,
                provider_in_time=provider_in_time,
                first_token_time=first_token_time,
                provider_end_time=provider_end_time,
                response_out_time=response_out_time,
                **{}
            )
            await pg_log_dao.insert_request_meta_log(meta_log)

            if not config.enable_request_response_content_log:
                return
            # 记录请求内容  ###################################################
            await self.log_content_service.replace_chat_completion_message_param(
                messages, use_public_url=False, delete_base64_after_upload=True)

            request_body = {
                "messages": messages,
            }
            if tools:
                request_body["tools"] = tools
            reply_body = {
                "choices": choices,
            }
            body_log: LlmApiRequestBodyLog = LlmApiRequestBodyLog(
                id=meta_log.id,
                log_time=log_time,
                account_name=account_name,
                model_id=model_id,
                gen_api_path=gen_api_path,
                interact_mode=interact_mode,
                request_body=json.dumps(request_body, ensure_ascii=False),
                request_header="",  # todo: 请求 header
                reply_body=json.dumps(reply_body, ensure_ascii=False),
                reply_header="",  # todo: 响应 header
            )
            await pg_log_dao.insert_request_body_log(body_log)
        except Exception as e:
            logger.error(f"Failed to log request content. gen_req_id: {context.letsgen_req_id}, "
                         f"model_id: {context.model_id}, "
                         f"account: {context.identity.account_name}, "
                         f"request_path: {context.request_path}, "
                         f"error: {e}", exc_info=True)
