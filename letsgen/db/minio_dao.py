# -*- coding: utf-8 -*-
"""
# @File    : minio_connection.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-26 00:45
"""
import asyncio
import json
import logging
from datetime import timedelta
from io import BytesIO
from typing import Optional
import urllib.parse

from aiohttp import ClientResponse
from miniopy_async import Minio, S3Error

import letsgen.config as config

logger = logging.getLogger(__name__)

minio_client: Optional[Minio] = None

# 允许来自内网网段的访问策略
POLICY_JSON = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "LetsgenAllowSpecificInternalIPs",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{config.letsgen_minio_bucket_name}/*"
            ],
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": [
                        "192.168.0.0/16",
                        "172.16.0.0/12",
                        "10.0.0.0/8",
                        "127.0.0.1",
                        "::1"
                    ]
                }
            }
        }
    ]
}


async def get_minio_client() -> Minio:
    """获取 minio 客户端实例"""
    global minio_client
    if minio_client is not None:
        return minio_client
    minio_client = Minio(
        config.letsgen_minio_endpoint,
        access_key=config.letsgen_minio_access_key,
        secret_key=config.letsgen_minio_secret_key,
        secure=config.letsgen_minio_endpoint_secure,  # http for False, https for True
    )
    await check_and_make_bucket(minio_client, config.letsgen_minio_bucket_name)
    # 应由 minio 管理员配置,而不是每次启动都设置
    # await set_minio_policy(minio_client)
    return minio_client


async def set_minio_policy(client: Minio):
    """连接 MinIO 并设置存储桶策略的异步函数"""

    # 将 Python 字典转换为 JSON 字符串
    policy_str = json.dumps(POLICY_JSON)
    try:
        # 验证策略是否设置成功 (可选)
        current_policy_str = await client.get_bucket_policy(config.letsgen_minio_bucket_name)
        current_policy = json.loads(current_policy_str)

        # 检查策略中的第一个 Sid 是否匹配
        if current_policy.get("Statement", [{}])[0].get("Sid") == "LetsgenAllowSpecificInternalIPs":
            logger.info("✅ S3 policy already set! No changes made.")
        else:
            logger.warning("❌ S3 policy LetsgenAllowSpecificInternalIPs not found or mismatched. Updating policy...")
            # 调用 set_bucket_policy
            await client.set_bucket_policy(
                config.letsgen_minio_bucket_name,
                policy_str
            )
            logger.info("✅ S3 policy updated successfully.")

    except S3Error as e:
        logger.error(f"❌ S3 set policy error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"❌ S3 set_minio_policy error: {e}", exc_info=True)


async def close_minio_client():
    """关闭 minio 客户端连接"""
    global minio_client
    if minio_client is not None:
        await minio_client.close_session()
        minio_client = None
        logger.info("S3 client connection closed.")


async def check_and_make_bucket(client: Minio, bucket_name: str):
    """检查存储桶是否存在, 不存在则创建"""
    # 检查存储桶是否存在
    found = await client.bucket_exists(bucket_name)
    if not found:
        logger.info(f"S3 Bucket '{bucket_name}' not found. Creating it...")
        # 创建存储桶
        await client.make_bucket(bucket_name)
        logger.info(f"S3 Bucket '{bucket_name}' created successfully.")
    else:
        logger.info(f"S3 Bucket '{bucket_name}' already exists.")


async def upload_data(
    client: Minio,
    bucket_name: str,
    object_name: str,
    data_stream: BytesIO,
    content_type: str,  # 如果实在不知道,填: "application/octet-stream"
):
    """上传数据流到 S3 存储桶"""
    data_length = len(data_stream.getbuffer())
    result = await client.put_object(
        bucket_name,
        object_name,
        data=data_stream,
        length=data_length,
        content_type=content_type,
    )
    logger.info(f"S3 successfully uploaded data_stream to {object_name}, ETag: {result.etag}")


async def upload_large_file(
    client: Minio,
    bucket_name: str,
    object_name: str,
    file_path: str,
):
    """上传大文件到 S3 存储桶"""
    # fput_object 自动处理文件切块和分段上传
    result = await client.fput_object(
        bucket_name,
        object_name,
        file_path,
    )
    logger.info(f"S3 successfully uploaded local_file to {object_name}, ETag: {result.etag}, local_file {file_path}")


async def download_file(
    client: Minio,
    bucket_name: str,
    object_name: str,
    download_path: str,
    chunk_size=1 * 1024 * 1024,  # 每次读取 1MB
):
    """从 S3 存储桶下载文件到本地"""
    response = None
    try:
        # 获取文件对象
        response: Optional[ClientResponse] = await client.get_object(bucket_name, object_name)

        # 将文件内容写入本地文件
        with open(download_path, 'wb') as file_data:
            while True:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break
                file_data.write(chunk)
        logger.info(f"S3 successfully downloaded object: {object_name} to {download_path}")
    except Exception as err:
        logger.error(f"S3 error downloading object: {object_name} to {download_path}. error: {err}", exc_info=True)
        raise err
    finally:
        if response:
            # 必须关闭 response 以释放连接
            response.close()
            response.release()


async def get_internal_url(
    client: Minio,
    bucket_name: str,
    object_name: str,
    target_host: str = config.letsgen_minio_internal_url,
) -> str:
    """生成对象的内网访问链接"""
    custom_url = f"{target_host}/{bucket_name}/{object_name}"
    return custom_url


async def get_public_presigned_url(
    client: Minio,
    bucket_name: str,
    object_name: str,
    expire_after_seconds: int = 7 * 24 * 3600,
    target_host: str = config.letsgen_minio_internal_url,
) -> str:
    """生成对象的预签名下载链接"""
    try:
        td = timedelta(seconds=expire_after_seconds)
        # 生成一个 7 天有效的预签名下载链接
        s3_url = await client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=td
        )

        parsed_url = urllib.parse.urlparse(s3_url)
        # target_host 格式应为 https://s3.example.com 或 http://192.168.1.10:9000
        custom_url = f"{target_host}{parsed_url.path}?{parsed_url.query}"
        logger.info(f"S3 presigned URL for object: {object_name} expires after {td}. url: {custom_url}")
        return custom_url
    except Exception as err:
        logger.error(f"S3 error generating presigned url. object: {object_name}. error: {err}", exc_info=True)
        raise err
