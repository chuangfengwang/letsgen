# -*- coding: utf-8 -*-
"""
# @File    : distributed_concurrency_middleware.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-27 11:47
"""
import asyncio
import json
import logging
import time
from typing import Set, Tuple, Dict

from fastapi import Request
from redis.asyncio import StrictRedis as AsyncStrictRedis
from starlette.types import ASGIApp, Scope, Receive, Send

import letsgen.config as config
import letsgen.db.redis_dao as redis_dao
import letsgen.service.auth_service as auth_service
import letsgen.utils.codec_util as codec_util
from letsgen.exceptions import error_class

logger = logging.getLogger(__name__)


class DistributeCurrencyCounter:
    # 心跳key. zset 结构
    HEARTBEAT_KEY = "letsgen-instance:heartbeat"
    # in-flight 请求记录 key. zset 结构
    CURRENCY_KEY_FORMAT = "letsgen-currency:{}"

    def __init__(self, redis_conn: AsyncStrictRedis, instance_id: str, instance_ttl: int):
        self.redis_conn = redis_conn
        self.instance_id = instance_id
        # redis 心跳保持信号存活时间,单位:毫秒
        self.instance_ttl = instance_ttl
        # 保留后台任务的强引用,避免被垃圾回收
        self._heartbeat_task = None
        self._background_tasks = set()

    async def async_init(self):
        # 提交心跳保持任务
        self._heartbeat_task = asyncio.create_task(self.heartbeat_loop_run())
        self._heartbeat_task.add_done_callback(self._background_tasks.discard)
        logger.info(f"{self.__class__.__name__} start heartbeat task: {self._heartbeat_task}")

    async def async_close(self):
        # 关闭心跳保持任务
        self._heartbeat_task.cancel()
        try:
            await self._heartbeat_task
        except asyncio.CancelledError:
            pass
        logger.info(f"{self.__class__.__name__} closing heartbeat task: {self._heartbeat_task}")
        # 清除当前实例心跳
        try:
            await self.redis_conn.zrem(DistributeCurrencyCounter.HEARTBEAT_KEY, self.instance_id)
            logger.info(f"{self.__class__.__name__} deleted heartbeat instance_id: {self.instance_id}")
        except Exception as e:
            logger.error(f"heartbeat delete failed. error=", exc_info=True)

    async def heartbeat_loop_run(self):
        """实例心跳维护任务"""
        while True:
            try:
                # 加入/更新时间戳
                now = time.time()
                expire_ts = now + self.instance_ttl / 1000.
                await self.redis_conn.zadd(
                    DistributeCurrencyCounter.HEARTBEAT_KEY, {self.instance_id: expire_ts})
                # 删掉旧时间戳
                now = time.time()
                await self.redis_conn.zremrangebyscore(
                    DistributeCurrencyCounter.HEARTBEAT_KEY, "-inf", now)
                logger.info(f"{self.__class__.__name__} update heartbeat. instance_id: {self.instance_id}")
            except Exception as e:
                logger.error(f"heartbeat update failed. error=", exc_info=True)
            await asyncio.sleep(max(self.instance_ttl / 1000 / 2 - 0.5, 0))  # 半TTL刷新一次

    async def fetch_alive_instances(self) -> Set[str]:
        """获取当前存活的实例ID列表"""
        alive_instances = set()
        now = time.time()
        instance_list = await self.redis_conn.zrangebyscore(DistributeCurrencyCounter.HEARTBEAT_KEY, now, "+inf")
        alive_instances.update(instance_list)
        return alive_instances

    def _request_zset_key(self, key: str):
        return DistributeCurrencyCounter.CURRENCY_KEY_FORMAT.format(key)

    def _request_zset_member(self, req_id: str):
        return f"{self.instance_id}-{req_id}"

    def request_member_parse(self, member: str) -> Tuple[str, str]:
        """
        解析 member 字段
        :param member: str, 记录在 zset 中的 key. 格式由 _request_zset_member 定义
        :return: 二元组, (实例id, 请求id)
        """
        pieces = member.split("-")
        return pieces[0], pieces[1]

    async def cleanup_zombie_request(self, key: str):
        """清理过期请求记录 和 失效心跳实例的请求记录"""
        zset_key = self._request_zset_key(key)
        now = time.time()

        # 1. 清理自然过期的请求
        await self.redis_conn.zremrangebyscore(zset_key, "-inf", now)

        # 2. 获取活跃实例
        alive_instances = await self.fetch_alive_instances()

        # 3. 找到僵尸请求
        members = await self.redis_conn.zrangebyscore(zset_key, now, "+inf")
        zombies = [m for m in members if self.request_member_parse(m)[0] not in alive_instances]
        if zombies:
            await self.redis_conn.zrem(zset_key, *zombies)
            logger.info(f"zombie request removed. len: {len(zombies)}. zombies: {zombies!r}")
        logger.info(f"cleanup_zombie_request finished. key: {key}")

    async def enter_request(self, key: str, request_ttl: float) -> str:
        letsgen_req_id = codec_util.gen_uuid_base64()
        logger.info(f"enter_request start. key: {key}, letsgen_req_id: {letsgen_req_id}")

        member = self._request_zset_member(letsgen_req_id)
        zset_key = self._request_zset_key(key)
        # 注册本次请求
        now = time.time()
        expire_ts = now + request_ttl / 1000.
        await self.redis_conn.zadd(zset_key, {member: expire_ts})
        return letsgen_req_id

    async def leave_request(self, key: str, req_id: str):
        # 请求完成，删除记录
        member = self._request_zset_member(req_id)
        zset_key = self._request_zset_key(key)
        await self.redis_conn.zrem(zset_key, member)
        logger.info(f"leave_request zrem ok. key: {key}, req_id: {req_id}")

        # 提交清理僵尸请求任务
        task = asyncio.create_task(self.cleanup_zombie_request(key))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

        logger.info(f"leave_request end. key: {key}, req_id: {req_id}")

    async def fetch_request_concurrency(self, key: str) -> int:
        """查询指定 key 的并发数"""
        zset_key = self._request_zset_key(key)
        now = time.time()
        # 统计并发数
        concurrency = await self.redis_conn.zcount(zset_key, now, "+inf")
        return concurrency

    async def fetch_all_instance_currency(self) -> Dict[str, int]:
        """查询所有实例的并发数. notice: 慢操作,慎用"""
        instance_concurrency_dict: Dict[str, int] = dict()
        now = time.time()
        async for key in self.redis_conn.scan_iter(DistributeCurrencyCounter.CURRENCY_KEY_FORMAT.format("*")):
            members = await self.redis_conn.zrangebyscore(key, now, "+inf")
            for m in members:
                instance, req_id = self.request_member_parse(m)
                instance_concurrency_dict.setdefault(instance, 0)
                instance_concurrency_dict[instance] += 1
        return instance_concurrency_dict


class DistributeCurrencyContext:
    """分布式并发上下文管理器"""

    def __init__(self, counter: DistributeCurrencyCounter, key: str, request_ttl: int):
        self.counter = counter
        self.key = key
        # 请求等待最大时间,单位: 毫秒
        self.request_ttl: int = request_ttl
        self.letsgen_req_id = None

    async def __aenter__(self):
        self.letsgen_req_id = await self.counter.enter_request(key=self.key, request_ttl=self.request_ttl)
        return self.letsgen_req_id

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.counter.leave_request(key=self.key, req_id=self.letsgen_req_id)


# 分布式全局计数器
llm_api_account_counter = DistributeCurrencyCounter(
    redis_conn=redis_dao.get_async_redis_conn(),
    instance_id=codec_util.gen_uuid_base64(),
    instance_ttl=config.llm_api_max_timeout
)


class ConcurrencyLimitMiddleware:
    """并发中间件（纯 ASGI 实现）"""

    def __init__(self, app: ASGIApp):
        self.app = app

    @classmethod
    async def cls_async_init(cls):
        await llm_api_account_counter.async_init()

    @classmethod
    async def cls_async_close(cls):
        await llm_api_account_counter.async_close()

    @classmethod
    def get_counter(cls) -> DistributeCurrencyCounter:
        return llm_api_account_counter

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 检查是否需要并发控制
        if scope["path"] not in config.letsgen_llm_api:
            await self.app(scope, receive, send)
            return
        # 跳过 OPTIONS 请求
        if scope.get("method", "").upper() == "OPTIONS":
            await self.app(scope, receive, send)
            return

        # 缓存请求体
        body_chunks = []
        body_bytes = b""

        async def receive_with_cache():
            nonlocal body_bytes
            message = await receive()
            if message["type"] == "http.request":
                body_chunk = message.get("body", b"")
                body_chunks.append(body_chunk)
                body_bytes += body_chunk
            return message

        # 创建 Request 对象用于读取
        cached_request = Request(scope, receive_with_cache)

        # 读取请求体
        full_body = await cached_request.body()

        # 获取 account
        account = await auth_service.get_account(cached_request)

        # 获取 model_id
        model_id = ""
        if full_body:
            try:
                json_body = json.loads(full_body.decode("utf-8"))
                model_id = json_body.get("model", "")
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        # todo: only for debug
        if not model_id:
            # 从查询参数获取
            query_string = scope.get("query_string", b"").decode()
            if query_string:
                from urllib.parse import parse_qs
                params = parse_qs(query_string)
                model_id = params.get("model", [""])[0]
            if not model_id:
                raise error_class.LlmParamError("can not find model_id")

        if not account:
            # 从查询参数获取
            query_string = scope.get("query_string", b"").decode()
            if query_string:
                from urllib.parse import parse_qs
                params = parse_qs(query_string)
                account = params.get("account", [""])[0]
            if not account:
                raise error_class.LlmParamError("can not find account")

        # 并发控制维度: 账号+模型
        control_key = f"{account}-{model_id}"

        # 创建 replay receive 函数
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

        # 在并发控制上下文中执行
        async with DistributeCurrencyContext(
            counter=llm_api_account_counter,
            key=control_key,
            request_ttl=config.llm_api_max_timeout,
        ):
            await self.app(scope, replay_receive, send)
