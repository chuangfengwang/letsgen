# -*- coding: utf-8 -*-
"""
# @File    : log_content_service.py
# @Desc    : 请求内容日志服务
# @Author  : chuangfeng.wang
# @Time    : 2025-12-08 00:22
"""
import base64
import mimetypes
import uuid
from datetime import datetime
from io import BytesIO
from typing import Tuple, Literal

import letsgen.config as config
import letsgen.db.minio_dao as minio_dao

# 写入 S3 的数据源类型: 输入还是输出
S3DataSourceType = Literal["I", "O"]


class LogContentService:
    """请求内容日志服务"""

    def __init__(self):
        self.minio_client = None

    async def async_init(self):
        # 获取 MinIO 客户端
        self.minio_client = await minio_dao.get_minio_client()

    def parse_base64_mime_type_and_content(self, base64_content: str) -> Tuple[str | None, str]:
        """解析 base64 编码内容的 MIME 类型和内容部分"""
        try:
            header, content = base64_content.split(',', 1)
            if header.startswith('data:') and ';base64' in header:
                mime_type = header[5:header.index(';base64')]
                return mime_type, content
        except Exception:
            return None, base64_content
        return None, base64_content

    def build_object_name(self, mime_type: str, in_or_out: S3DataSourceType) -> str:
        """根据 MIME 类型构建对象名称"""
        extension = mimetypes.guess_extension(mime_type, strict=True) if mime_type else ''
        # mimetypes 模块对部分文件支持不完整或不是期望类型，这里添加一些常见映射
        custom_mime_map = {
            'application/xml': '.xml',  # 确保 XML 正确
        }
        # 如果 mimetypes 没有找到，或者我们有更明确的自定义映射，则使用自定义映射
        if mime_type in custom_mime_map:
            extension = custom_mime_map[mime_type]
        dt_prefix = datetime.now().strftime("%Y%m/%dT%H")
        object_name = f"{dt_prefix}{in_or_out}/{uuid.uuid4().hex}{extension}"
        return object_name

    async def upload_base64_content(self, base64_content: str, in_or_out: S3DataSourceType) -> str:
        """上传 base64 编码的内容到 S3, 返回文件对象名"""
        # 解析 base64 内容的 MIME 类型和实际内容
        mime_type, content = self.parse_base64_mime_type_and_content(base64_content)

        # 解码 base64 内容
        binary_data = base64.b64decode(content)
        data_stream = BytesIO(binary_data)

        object_name = self.build_object_name(mime_type, in_or_out)
        # 上传数据
        await minio_dao.upload_data(
            client=self.minio_client,
            bucket_name=config.letsgen_minio_bucket_name,
            object_name=object_name,
            data_stream=data_stream,
            content_type=mime_type if mime_type else "application/octet-stream"
        )
        return object_name
