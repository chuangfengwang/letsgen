# -*- coding: utf-8 -*-
"""
# @File    : e2e_tracelog_middleware.py
# @Desc    : 端到端调用链日志中间件
# @Author  : chuangfeng.wang
# @Time    : 2025-08-25 21:48
"""
import json
import logging
import time
from typing import Dict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

import letsgen.utils.util as util

logger = logging.getLogger(__name__)


class RequestResponseLogger(BaseHTTPMiddleware):

    def filter_log_headers(self, request: Request) -> Dict[str, str]:
        """哪些 header 需要记录到日志里"""
        log_headers = {}
        for key, value in request.headers.items():
            if key.upper().startswith('X-'):
                log_headers[key] = value
        return log_headers

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        qtrace_id = request.headers.get("qtraceid")
        if not qtrace_id:
            qtrace_id = util.gen_uuid()
        request.state.qtrace_id = qtrace_id  # 将 trace_id 存入state，方便后续在路由中使用或关联

        log_data = {
            "qtraceid": qtrace_id,
            "type": "http_request",
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": request.client.host if request.client else "N/A",
            "query_param": dict(request.query_params),
            "headers": self.filter_log_headers(request),
            "body": None,
        }

        # 尝试读取请求体
        try:
            # 读取请求体，FastAPI 的 Request 对象会缓存 body，所以后续路由中仍可访问. todo: really?
            try:
                # 尝试解码为JSON
                log_data["body"] = await request.json()
            except json.JSONDecodeError:
                # 非JSON体，尝试解码为文本，如果失败则存为原始字节的表示
                body = await request.body()
                if body:
                    log_data["body"] = body.decode('utf-8', errors='ignore')
                else:
                    log_data["body"] = None

        except Exception as e:
            logger.warning(f"Failed to read request body for {qtrace_id}: {e}", exc_info=True)
            log_data["body"] = "ERROR: Could not read body"

        logger.info(f"Incoming Request. log_data: {json.dumps(log_data, ensure_ascii=False)}")

        try:
            response = await call_next(request)
            original_body_iterator = response.body_iterator  # 获取原始响应体的迭代器

            # 定义一个新的异步生成器，用于包装原始迭代器
            async def logging_body_iterator():
                chunk_num = 0
                async for chunk in original_body_iterator:
                    chunk_num += 1

                    # 记录每个chunk的信息
                    chunk_content_preview = ""
                    try:
                        # 尝试解码为UTF-8，但要注意可能不是完整的有效文本
                        try:
                            chunk_content_preview = json.loads(chunk.decode('utf-8', errors='ignore'))
                        except json.JSONDecodeError:
                            chunk_content_preview = chunk.decode('utf-8', errors='ignore')
                    except Exception:
                        chunk_content_preview = f"<binary chunk of {len(chunk)} bytes>"
                    chunk_info = {
                        "qtraceid": qtrace_id,
                        "chunk_number": chunk_num,
                        "chunk_size_bytes": len(chunk),
                        "chunk_content_preview": chunk_content_preview,
                        "status_code": response.status_code,  # 添加响应状态码作为上下文
                        "content_type": response.media_type,  # 添加内容类型
                    }
                    logger.info(
                        f"Response Chunk Logged. chunk_info: {json.dumps(chunk_info, ensure_ascii=False)}"
                    )
                    yield chunk  # 将 chunk 传递给下一个消费者（通常是Uvicorn）

            # 将原始响应的body_iterator替换为我们带日志功能的迭代器
            response.body_iterator = logging_body_iterator()

            # 记录响应的元数据 (不包含完整的响应体，因为体是流式处理的)
            process_time = (time.time() - start_time) * 1000
            response_metadata_log_data = {
                "qtraceid": qtrace_id,
                "type": "http_response_metadata",
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_time_ms": process_time,
            }
            logger.info(f"Outgoing Response Metadata. log_data: "
                        f"{json.dumps(response_metadata_log_data, ensure_ascii=False)}")

            return response  # 返回被修改的响应对象

        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            error_log_data = {
                "qtraceid": qtrace_id,
                "type": "http_error",
                "error_message": str(e),
                "response_time_ms": process_time,
            }
            logger.error(f"Request Processing Error. log_data: {json.dumps(error_log_data, ensure_ascii=False)}",
                         exc_info=True)
            raise  # 重新抛出异常，让FastAPI的异常处理机制处理
