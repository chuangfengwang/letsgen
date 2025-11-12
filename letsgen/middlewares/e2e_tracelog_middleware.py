# -*- coding: utf-8 -*-
"""
# @File    : e2e_tracelog_middleware.py
# @Desc    : 端到端调用链日志中间件
# @Author  : chuangfeng.wang
# @Time    : 2025-08-25 21:48
"""
import json
import logging
from datetime import datetime

from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.types import ASGIApp, Scope, Receive, Send

import letsgen.config as config
import letsgen.entity.llm_entity as openai_entity
import letsgen.utils.codec_util as codec_util
import letsgen.utils.datatime_util as datatime_util

logger = logging.getLogger(__name__)


class RequestResponseLogger:
    """纯 ASGI 中间件，避免 BaseHTTPMiddleware 的限制"""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 创建 Request 对象用于读取请求信息
        # request = Request(scope, receive)

        # 设置 context
        # 使用时, 先进行类型提示转换, 获得 ide 智能提示能力:
        # context = cast(LlmRequestContext, request.state.context)
        context = openai_entity.LlmRequestContext(**{})
        scope["state"] = {"context": context}

        # 构造 context 各个参数
        request_in_dt = context.mark_event_dt("request_in")
        context.letsgen_req_id = codec_util.gen_uuid()
        headers = Headers(scope=scope)
        context.trace_id = headers.get("qtraceid", default=context.letsgen_req_id)
        context.request_path = scope["path"]
        context.request_method = scope["method"]
        client = scope.get("client")
        client_ip = client[0] if client else "N/A"
        context.client_ip = client_ip
        context.proj_id = headers.get("project", "")

        # 读取请求体
        body_param = None
        body_bytes = b""

        # 创建一个新的 receive 函数来缓存请求体
        body_chunks = []

        async def receive_with_cache():
            nonlocal body_bytes
            message = await receive()
            if message["type"] == "http.request":
                body_chunk = message.get("body", b"")
                body_chunks.append(body_chunk)
                body_bytes += body_chunk
            return message

        # 使用缓存的 receive
        cached_request = Request(scope, receive_with_cache)

        # 读取请求体用于日志
        try:
            # 完全读取请求体
            full_body = await cached_request.body()
            if full_body:
                try:
                    body_param = json.loads(full_body.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body_param = full_body.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Failed to read request body. trace_id: {context.trace_id}", exc_info=True)
            body_param = "<ERROR: Could not read body>"

        context.origin_body_param = body_param if isinstance(body_param, dict) else None

        # 记录请求日志
        log_data = {
            "letsgen_req_id": context.letsgen_req_id,
            "qtraceid": context.trace_id,
            "type": "http_request",
            "request_in_dt": datatime_util.datetime_to_str(request_in_dt),
            "proj_id": context.proj_id,
            "method": scope["method"],
            "path": scope["path"],
            "client_ip": client_ip,
            "query_param": dict(scope.get("query_string", {})),
            "headers": {k: v for k, v in headers.items() if k.upper().startswith('X-')},
            "body": body_param,
        }
        logger.info(f"Incoming Request. log_data: {json.dumps(log_data, ensure_ascii=False)}")

        # 创建新的 receive 函数，使用缓存的请求体
        body_sent = False
        body_index = 0

        async def replay_receive():
            nonlocal body_sent, body_index
            if not body_sent:
                if body_index < len(body_chunks):
                    chunk = body_chunks[body_index]
                    body_index += 1
                    more_body = body_index < len(body_chunks)
                    return {"type": "http.request", "body": chunk, "more_body": more_body}
                else:
                    body_sent = True
                    return {"type": "http.request", "body": b"", "more_body": False}
            # 请求体发送完毕后，继续监听断开连接
            return await receive()

        # 包装 send 以记录响应
        response_started = False
        status_code = None
        response_headers = {}
        chunk_num = 0

        async def send_with_logging(message):
            nonlocal response_started, status_code, response_headers, chunk_num

            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                response_headers = {k.decode(): v.decode() for k, v in message.get("headers", [])}

                # 记录响应元数据
                response_out_dt = context.mark_event_dt("response_out")
                process_time = datatime_util.timedelta_to_milliseconds((datetime.now() - request_in_dt))
                response_metadata_log_data = {
                    "qtraceid": context.trace_id,
                    "type": "http_response_metadata",
                    "request_in_dt": datatime_util.datetime_to_str(request_in_dt),
                    "response_out_dt": datatime_util.datetime_to_str(response_out_dt),
                    "process_time": process_time,
                    "proj_id": context.proj_id,
                    "status_code": status_code,
                    "headers": response_headers,
                }
                logger.info(f"Outgoing Response Metadata. log_data: "
                            f"{json.dumps(response_metadata_log_data, ensure_ascii=False)}")

            elif message["type"] == "http.response.body" \
                and config.debug_flag \
                and scope["path"] in config.letsgen_llm_api:
                body = message.get("body", b"")
                if body:
                    chunk_num += 1
                    # 记录响应 chunk
                    chunk_content_preview = ""
                    try:
                        chunk_content_preview = body.decode('utf-8', errors='ignore')
                    except Exception:
                        chunk_content_preview = f"<binary chunk of {len(body)} bytes>"

                    chunk_meta_info = {
                        "letsgen_req_id": context.letsgen_req_id,
                        "qtraceid": context.trace_id,
                        "proj_id": context.proj_id,
                        "chunk_number": chunk_num,
                        "chunk_size_bytes": len(body),
                        "status_code": status_code,
                        "content_type": response_headers.get("content-type", ""),
                    }
                    logger.info(
                        f"Response Chunk Logged. chunk_meta_info: {json.dumps(chunk_meta_info, ensure_ascii=False)}. "
                        f"chunk_content_preview: {chunk_content_preview.rstrip()}")

            await send(message)

        try:
            await self.app(scope, replay_receive, send_with_logging)
        except Exception as e:
            process_time = datatime_util.timedelta_to_milliseconds((datetime.now() - request_in_dt))
            error_log_data = {
                "qtraceid": context.trace_id,
                "type": "http_error",
                "proj_id": context.proj_id,
                "error_message": str(e),
                "response_time_ms": process_time,
            }
            logger.error(f"Request Processing Error. log_data: {json.dumps(error_log_data, ensure_ascii=False)}",
                         exc_info=True)
            raise
