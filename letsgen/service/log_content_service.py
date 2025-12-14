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
from typing import Tuple, Literal, Iterable

from openai.types.chat import ChatCompletionMessageParam

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

    @staticmethod
    def parse_base64_mime_type_and_content(base64_content: str) -> Tuple[str | None, str]:
        """解析 base64 编码内容的 MIME 类型和内容部分"""
        try:
            header, content = base64_content.split(',', 1)
            if header.startswith('data:') and ';base64' in header:
                mime_type = header[5:header.index(';base64')]
                return mime_type, content
        except Exception:
            return None, base64_content
        return None, base64_content

    @staticmethod
    def parse_mime_file_extension(mime_type: str) -> str | None:
        """根据 MIME 类型解析文件扩展名"""
        extension = mimetypes.guess_extension(mime_type, strict=True) if mime_type else ''
        # mimetypes 模块对部分文件支持不完整或不是期望类型，这里添加一些常见映射
        custom_mime_map = {
            'application/xml': '.xml',  # 确保 XML 正确
        }
        # 如果 mimetypes 没有找到，或者我们有更明确的自定义映射，则使用自定义映射
        if mime_type in custom_mime_map:
            extension = custom_mime_map[mime_type]
        return extension

    @staticmethod
    def generate_object_name(extension: str, in_or_out: S3DataSourceType) -> str:
        """根据文件后缀类型生成一个对象名称"""
        dt_prefix = datetime.now().strftime("%Y%m/%dT%H")
        object_name = f"{config.letsgen_minio_object_prefix}{dt_prefix}{in_or_out}/{uuid.uuid4().hex}{extension}"
        return object_name

    async def upload_base64_content(
        self, base64_content: str, in_or_out: S3DataSourceType, known_extension: str | None = None
    ) -> str:
        """上传 base64 编码的内容到 S3, 返回文件对象名"""
        # 解析 base64 内容的 MIME 类型和实际内容
        mime_type, content = self.parse_base64_mime_type_and_content(base64_content)

        # 解码 base64 内容
        binary_data = base64.b64decode(content)
        data_stream = BytesIO(binary_data)

        extension = known_extension if known_extension else \
            self.parse_mime_file_extension(mime_type) if mime_type else ''
        object_name = self.generate_object_name(extension, in_or_out)
        # 上传数据
        await minio_dao.upload_data(
            client=self.minio_client,
            bucket_name=config.letsgen_minio_bucket_name,
            object_name=object_name,
            data_stream=data_stream,
            content_type=mime_type if mime_type else "application/octet-stream"
        )
        return object_name

    async def presign_internal_url_for_object(self, object_name: str) -> str:
        """获取对象的内网预签名 URL"""
        url = await minio_dao.get_internal_url(
            client=self.minio_client,
            bucket_name=config.letsgen_minio_bucket_name,
            object_name=object_name,
            target_host=config.letsgen_minio_internal_url,
        )
        return url

    async def presign_public_url_for_object(self, object_name: str) -> str:
        """获取对象的内网预签名 URL"""
        url = await minio_dao.get_public_presigned_url(
            client=self.minio_client,
            bucket_name=config.letsgen_minio_bucket_name,
            object_name=object_name,
            expire_after_seconds=config.letsgen_minio_public_expire,
            target_host=config.letsgen_minio_public_url,
        )
        return url

    async def replace_chat_completion_message_param(
        self,
        messages: Iterable[ChatCompletionMessageParam],
        use_public_url: bool = False,
        delete_base64_after_upload: bool = False,
    ):
        """替换 ChatCompletionMessageParam 列表中的 base64 内容为预签名 URL"""
        for message in messages:
            if 'content' in message and isinstance(message['content'], str):
                continue
            if 'content' in message and isinstance(message['content'], list):
                for part in message['content']:
                    if 'type' in part and part['type'] == 'text':
                        continue
                    # 把 base64 图片上传替换为预签名 URL
                    if 'type' in part and part['type'] == 'image_url':
                        if part['image_url']['url'].startswith('data:') and ';base64' in part['image_url']['url']:
                            object_name = await self.upload_base64_content(part['image_url']['url'], 'I')
                            url = await self.presign_public_url_for_object(object_name) if use_public_url \
                                else await self.presign_internal_url_for_object(object_name)
                            part['image_url']['url'] = url
                        continue
                    # 把 base64 语音上传, 并添加预签名 URL
                    elif 'type' in part and part['type'] == 'input_audio':
                        base64_data = part['input_audio']['data']
                        data_type = part['input_audio']['format']
                        object_name = await self.upload_base64_content(base64_data, 'I',
                                                                       known_extension=f".{data_type}")
                        url = await self.presign_public_url_for_object(object_name) if use_public_url \
                            else await self.presign_internal_url_for_object(object_name)
                        part['input_audio']['url'] = url
                        if delete_base64_after_upload:
                            part['input_audio']['data'] = ''
                    # 把 base64 文件上传, 并添加预签名 URL 字段
                    elif 'type' in part and part['type'] == 'file':
                        base64_data = part['file']['data']
                        filename = part['file']['filename']
                        extension = ''
                        if '.' in filename:
                            extension = filename[filename.rindex('.'):]
                        object_name = await self.upload_base64_content(base64_data, 'I', known_extension=extension)
                        url = await self.presign_public_url_for_object(object_name) if use_public_url \
                            else await self.presign_internal_url_for_object(object_name)
                        part['file']['url'] = url
                        if delete_base64_after_upload:
                            part['file']['data'] = ''
