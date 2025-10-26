# -*- coding: utf-8 -*-
"""
# @File    : password_util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 22:12
"""
from __future__ import annotations

import base64
import datetime
from typing import Dict, Any, List
import logging

import bcrypt
import jwt
from Crypto.Cipher import AES

import letsgen.config as config

# jwt 加密算法: HS256
JWT_ALGORITHM = "HS256"

logger = logging.getLogger(__name__)


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行哈希加密
    :param plain_password: 明文密码
    :return: 哈希加密后的密码
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    hashed_str = hashed.decode('utf-8')
    return hashed_str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配
    :param plain_password: 明文密码
    :param hashed_password: 哈希加密后的密码
    :return: 是否匹配
    """
    is_valid = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    return is_valid


def add_str_to_multiple_len(text: str, modulo_len=16) -> bytes:
    """
    如果 text 不是 modulo_len 的倍数那就补足为 modulo_len 的倍数
    :param text: 需要加密的参数文本
    :param modulo_len: 指定参数的位数
    :return: 补足位数的文本的字节形式
    """
    if modulo_len <= 0:
        modulo_len = 1
    if len(text) % modulo_len != 0:
        text += '\0' * (modulo_len - len(text) % modulo_len)
    return text.encode(encoding='utf-8')


def encrypt_aes(plain_text: str, aes_key: str = config.letsgen_encryption_key) -> str:
    """
    aes的ecb模式加密
    :param plain_text: 加密数据
    :param aes_key: 加密的秘钥
    :return: 加密之后的密文
    """
    # 初始化加密器
    aes = AES.new(add_str_to_multiple_len(aes_key, 16), AES.MODE_ECB)
    # 先进行aes加密
    encrypt = aes.encrypt(add_str_to_multiple_len(plain_text, 16))
    # 用base64转成字符串形式
    encrypted_text = str(base64.b64encode(encrypt), encoding='utf-8')  # 执行加密并转码返回bytes
    return encrypted_text.strip()


def decrypt_aes(encrypted_text: str, aes_key: str = config.letsgen_encryption_key) -> str:
    """
    aes 的 ecb 模式解密
    :param encrypted_text: 待解密数据文本
    :param aes_key: 加密的秘钥
    :return: 解密之后的数据文本
    """
    # 初始化加密器
    aes = AES.new(add_str_to_multiple_len(aes_key, 16), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(add_str_to_multiple_len(encrypted_text, 16))
    # 执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return decrypted_text.strip()


def create_jwt(user_name: str, role_list: List[str], expire_after_minutes: float) -> str:
    """
    颁发 JWT Token
    """
    # 1. 定义 Payload (载荷)
    # iat: Issued At (签发时间)
    # exp: Expiration Time (过期时间) - 推荐设置，以提高安全性
    # sub: Subject (主题) - 通常是用户ID
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "user_name": user_name,
        "role": role_list,
        "iat": now,  # 签发时间
        "exp": now + datetime.timedelta(minutes=expire_after_minutes),  # 过期时间
    }

    # 2. 编码生成 Token
    encoded_jwt = jwt.encode(
        payload,
        config.letsgen_jwt_secret_key,
        algorithm=JWT_ALGORITHM
    )

    return encoded_jwt


def verify_jwt(token: str) -> Dict[str, Any] | None:
    """
    验证 JWT Token 并返回 Payload
    """
    try:
        # 1. 解码和验证 Token
        # 验证过程会自动检查签名是否有效、Token是否过期等
        payload = jwt.decode(
            token,
            config.letsgen_jwt_secret_key,
            algorithms=[JWT_ALGORITHM],
            leeway=0,
        )
        return payload
    except jwt.ExpiredSignatureError:
        # 签名已过期
        logger.error(f"jwt token expired. token: {token}")
        return None
    except jwt.InvalidSignatureError:
        # 签名无效 (Token被篡改或使用了错误的密钥)
        logger.error(f"jwt token signature error. token: {token}")
        return None
    except jwt.InvalidTokenError as e:
        # 其他无效 Token 错误
        logger.error(f"jwt token invalid error. token: {token}")
        return None
