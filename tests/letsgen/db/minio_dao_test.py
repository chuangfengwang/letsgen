# -*- coding: utf-8 -*-
"""
# @File    : minio_dao_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-12-06 12:53
"""
import asyncio
import os

import pytest
import pytest_asyncio

from letsgen.db.minio_dao import *


@pytest_asyncio.fixture
async def async_fetch_connection():
    # 异步数据库连接
    print("\nSetting up async minio connection...")
    client = await get_minio_client()
    yield client
    # 异步关闭连接
    print("\nClosing async minio connection...")
    await client.close_session()


@pytest.mark.asyncio
async def test_upload_data(async_fetch_connection):
    client = async_fetch_connection
    data = "Hello, MinIO!"
    data_stream = BytesIO(data.encode())
    await upload_data(
        client,
        config.letsgen_minio_bucket_name,
        "example/hello.txt",
        data_stream,
        "text/plain"
    )
    print()
    print("Upload data test completed.")


@pytest.mark.asyncio
async def test_get_presigned_url(async_fetch_connection):
    client = async_fetch_connection
    url = await get_presigned_url(
        client,
        config.letsgen_minio_bucket_name,
        "example/hello.txt",
        expire_after_seconds=3600  # 1 hour
    )
    print()
    print(f"Presigned URL: {url}")
    print("Get presigned URL test completed.")


@pytest.mark.asyncio
async def test_download_file(async_fetch_connection):
    client = async_fetch_connection
    await download_file(
        client,
        config.letsgen_minio_bucket_name,
        "example/hello.txt",
        os.path.join(config.cur_dir, "tmp", "downloaded_hello.txt")
    )
    print()
    print("Download file test completed.")


@pytest.mark.asyncio
async def test_upload_large_file(async_fetch_connection):
    client = async_fetch_connection
    await upload_large_file(
        client,
        config.letsgen_minio_bucket_name,
        "example/large_file.html",
        os.path.join(config.project_dir, "gateway-ui/demo-chat-4.html")
    )
    print()
    print("Upload large file test completed.")


async def main():
    client = await get_minio_client()
    async with client:
        # 示例：上传数据流
        data = "Hello, MinIO!"
        data_stream = BytesIO(data.encode())
        await upload_data(
            client,
            config.letsgen_minio_bucket_name,
            "example/hello.txt",
            data_stream,
            "text/plain"
        )

        # 示例：生成预签名 URL
        url = await get_presigned_url(
            client,
            config.letsgen_minio_bucket_name,
            "example/hello.txt",
            expire_after_seconds=3600  # 1 hour
        )
        print(f"Presigned URL: {url}")

        # 示例：下载文件
        await download_file(
            client,
            config.letsgen_minio_bucket_name,
            "example/hello.txt",
            "downloaded_hello.txt"
        )

        # 示例：上传大文件
        await upload_large_file(
            client,
            config.letsgen_minio_bucket_name,
            "example/large_file.html",
            "../../gateway-ui/demo-chat-4.html"
        )
    await client.close_session()


if __name__ == "__main__":
    # 运行主异步函数
    asyncio.run(main())
