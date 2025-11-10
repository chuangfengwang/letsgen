#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-16 00:03
"""
import base64
import datetime
import json
import re
import uuid
from dataclasses import is_dataclass, asdict
from enum import Enum
from typing import Dict
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def gen_uuid():
    """生成紧凑格式的 UUID"""
    uuid_output = str(uuid.uuid4()).replace("-", "")
    return uuid_output


def gen_uuid_base64() -> str:
    """生成 base64 格式的 UUID. 包含字符 + 和 / , 但不包含 = 号"""
    uuid_output = str(base64.b64encode(uuid.uuid4().bytes), 'utf-8').rstrip("=")
    return uuid_output


def _padding_to_base64(string: str) -> str:
    """用 = 补齐 base64 字符串长度到 4 的倍数长度"""
    return string + "=" * (len(string) - len(string) % 4)


def b64decode(string: str) -> bytes:
    """带 padding 补齐能力的 base64 解码器"""
    return base64.b64decode(_padding_to_base64(string).encode('utf-8'))


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        # 有特殊格式化需求的类型处理
        if isinstance(obj, datetime.datetime):
            # 将 datetime 对象转换为 ISO 8601 格式的字符串 "2024-05-29T18:58:37.168222"
            return obj.isoformat()
        if isinstance(obj, Enum):
            # enum 类型处理: 枚举类型.枚举值
            return '%s.%s' % (obj.__class__.__name__, obj.name)
        # 其他 object 类型的处理
        elif isinstance(obj, object):
            # 读取对象的所有非私有属性
            d = {
                cls_attr: getattr(obj, cls_attr) for cls_attr in dir(obj) if
                not cls_attr.startswith("__")  # 实际上不会有, 因为 dir() 不会返回双下划线开头的属性
                and not cls_attr.startswith("_")
                and not callable(getattr(obj, cls_attr))
            }
            return d
        return super().default(obj)


class PhoneNumberCipher:
    """
    对文本中的手机号码进行加解密操作。
    对11位手机号第4到7位(1-base)进行替换,替换位[a-zA-z0-9]的四位,且加密结果4位不全部是数字
    todo: 如果原字符串中恰巧出现加密后的字符串, 会导致解密还原错误
    """

    # 中国大陆手机号码的严格正则表达式
    PHONE_PATTERN: re.Pattern = re.compile(
        r"(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}"
    )
    # 占位符的固定长度
    PLACEHOLDER_LENGTH = 4

    def __init__(self):
        # 存储 '加密后的完整字符串': '原始手机号' 的映射，用于解密
        self.decryption_map: Dict[str, str] = {}
        # 存储 '原始手机号': '加密后的完整字符串' 的映射，用于避免重复加密
        self.encryption_map: Dict[str, str] = {}

    def _generate_safe_placeholder(self) -> str:
        """
        生成一个长度固定为 4，且至少包含一个非数字字符的唯一占位符。
        使用 UUID + Base64 编码来确保高熵和紧凑性。
        """
        while True:
            # 1. 使用 UUID 生成 16 字节的随机数
            random_bytes = uuid.uuid4().bytes

            # 2. Base64 编码
            # b64encode 返回 bytes，需要 decode('utf-8') 得到字符串
            b64_str = (base64.b64encode(random_bytes).decode('utf-8').rstrip('=')
                       .replace("+", "").replace("/", ""))
            if len(b64_str) < 4:
                continue

            # 3. 截取前 4 位字符作为占位符
            placeholder = b64_str[:self.PLACEHOLDER_LENGTH]

            # 4. 检查是否全是数字 (核心校验)
            if not placeholder.isdigit():
                # 如果不是纯数字（即包含 Base64 字符集中的字母或符号），则接受
                return placeholder

            # 如果是纯数字，则循环重新生成，直到满足条件

    def _encrypt_phone(self, match: re.Match) -> str:
        """
        供 re.sub 调用的替换函数，用于加密匹配到的手机号。
        将手机号：13911110001 替换为 139<4位Base64>0001。
        并记录映射关系。
        """
        full_phone = match.group(0)  # 完整的 11 位手机号

        # 1. 检查是否已经被加密过（在当前会话中）
        if full_phone in self.encryption_map:
            return self.encryption_map[full_phone]

        # 2. 执行加密操作
        prefix = full_phone[:3]  # 前三位
        suffix = full_phone[7:]  # 后四位

        # 生成唯一的、安全的 4 位占位符
        unique_placeholder = self._generate_safe_placeholder()

        # 加密后的形式：前缀 + 唯一占位符 + 后缀
        encrypted_phone_str = f"{prefix}{unique_placeholder}{suffix}"

        # 3. 存储映射关系
        self.decryption_map[encrypted_phone_str] = full_phone
        self.encryption_map[full_phone] = encrypted_phone_str

        logger.info(f"✅ 手机号加密: {full_phone} -> {encrypted_phone_str}")
        return encrypted_phone_str

    def encrypt_text(self, text: str) -> str:
        """
        对输入文本中的所有手机号进行加密。
        """
        encrypted_text = self.PHONE_PATTERN.sub(self._encrypt_phone, text)
        return encrypted_text

    def decrypt_text(self, text: str) -> str:
        """
        对输入文本中的加密手机号进行还原。
        使用字典查找和替换。
        """
        decrypted_text = text

        # 遍历所有存储的加密手机号（即包含 4 位 Base64 占位符的完整字符串），进行还原
        for encrypted_phone_str, original_phone in self.decryption_map.items():
            # 使用字符串替换，精确还原
            decrypted_text = decrypted_text.replace(encrypted_phone_str, original_phone)

        return decrypted_text
