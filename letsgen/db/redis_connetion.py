# -*- coding: utf-8 -*-
"""
# @File    : redis_connetion.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-26 00:45
"""


def async_single_conn(redis_url: str):
    from redis.asyncio import StrictRedis

    redis_conn = StrictRedis.from_url(
        redis_url,
        encoding="utf8",
        decode_responses=True,  # 可选：让返回值自动解码为字符串
        socket_timeout=5,  # socket 读写超时时间（秒）
        socket_connect_timeout=5,  # socket 连接超时时间（秒）
        socket_keepalive=True,  # 启用 TCP keepalive
        socket_keepalive_options={},  # 使用系统默认的 keepalive 配置
        retry_on_timeout=True,  # 超时时自动重试
        health_check_interval=30,  # 健康检查间隔（秒）
    )
    return redis_conn


def sync_single_conn(redis_url: str):
    from redis import StrictRedis

    redis_conn = StrictRedis.from_url(
        redis_url,
        encoding="utf8",
        decode_responses=True,  # 可选：让返回值自动解码为字符串
        socket_timeout=5  # 可选：设置连接超时时间
    )
    return redis_conn


def async_sentinel_conn():
    from redis.asyncio.sentinel import Sentinel
    sentinel_nodes = [
        ("127.0.0.1", 26379),
        ("127.0.0.1", 26380),
    ]
    master_name = "my-master"

    sentinel = Sentinel(
        sentinel_nodes,
        password="<PASSWORD>",
        socket_timeout=0.1,
        decode_responses=True
    )

    # 获取 master 节点的异步客户端
    master_client = sentinel.master_for(master_name)

    # 获取 replica 节点的异步客户端 (可选)
    # replica_client = await sentinel.slave_for(master_name)
    return master_client


def sync_sentinel_conn():
    from redis.sentinel import Sentinel
    sentinel_nodes = [
        ("127.0.0.1", 26379),
        ("127.0.0.1", 26380),
    ]
    master_name = "my-master"

    sentinel = Sentinel(
        sentinel_nodes,
        password="<PASSWORD>",
        socket_timeout=0.1,
        decode_responses=True
    )

    # 获取 master 节点的异步客户端
    master_client = sentinel.master_for(master_name)

    # 获取 replica 节点的异步客户端 (可选)
    # replica_client = await sentinel.slave_for(master_name)
    return master_client


async def async_cluster_conn():
    from redis.asyncio.cluster import ClusterNode
    from redis.asyncio.cluster import RedisCluster

    cluster_nodes = [
        ClusterNode("172.17.0.2", 6379, password="<PASSWORD>"),
        ClusterNode("172.17.0.3", 6379, password="<PASSWORD>"),
    ]
    redis_conn = await RedisCluster(
        startup_nodes=cluster_nodes,
        password=None,
        encoding="utf8",
        decode_responses=True,
    )
    return redis_conn


def sync_cluster_conn():
    from redis.cluster import ClusterNode
    from redis.cluster import RedisCluster

    cluster_nodes = [
        ClusterNode("172.17.0.2", 6379, ),
        ClusterNode("172.17.0.3", 6379, ),
    ]
    redis_conn = RedisCluster(
        startup_nodes=cluster_nodes,
        password=None,
        encoding="utf8",
        decode_responses=True,
    )
    return redis_conn
