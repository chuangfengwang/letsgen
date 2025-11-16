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
import logging
import os
from typing import Dict, Any, List

import bcrypt
import jwt
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

import letsgen.config as config

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


def encrypt_aes_ecb(plain_text: str, aes_key: str = config.letsgen_encryption_key) -> str:
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


def decrypt_aes_ecb(encrypted_text: str, aes_key: str = config.letsgen_encryption_key) -> str:
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


def _derive_key(password: str, salt: bytes) -> bytes:
    """
    密钥和盐值的处理函数: 使用 Scrypt 算法从密码派生出 256 位 (32 字节) 的 AES 密钥。

    参数:
        password (str): 用户密码或密钥字符串。
        salt (bytes): 随机盐值。

    返回:
        bytes: 32 字节的派生密钥。
    """
    # Scrypt 是一种高安全性的密码派生函数
    kdf = Scrypt(
        salt=salt,
        length=32,  # AES-256 需要 32 字节的密钥
        n=2 ** 14,  # CPU/内存成本参数
        r=8,  # 块大小参数
        p=1,  # 并行化参数
        backend=None
    )
    return kdf.derive(password.encode())


def encrypt_aes_gcm(plaintext: str, password: str = config.letsgen_encryption_key) -> str:
    """
    使用 AES-256-GCM 模式加密纯文本。

    加密结果包含：盐值 (salt)、初始化向量 (nonce/IV) 和密文 (ciphertext)，
    它们被拼接并用 Base64 编码后返回。

    参数:
        plaintext (str): 待加密的原始字符串。
        password (str): 用于密钥派生的密码字符串。

    返回:
        str: Base64 编码的加密结果字符串。
    """
    # 1. 生成随机盐值 (Salt)
    salt = os.urandom(16)

    # 2. 从密码派生出密钥
    key = _derive_key(password, salt)

    # 3. 生成随机初始化向量/Nonce (AES-GCM 推荐 12 字节)
    nonce = os.urandom(12)

    # 4. 创建 AES-GCM 对象
    aesgcm = AESGCM(key)

    # 5. 执行加密
    # associated_data (aad) 设为 None，也可以用于存储未加密但需要认证的数据
    ciphertext_with_tag = aesgcm.encrypt(
        nonce,
        plaintext.encode('utf-8'),
        associated_data=None
    )

    # 6. 拼接 salt, nonce, ciphertext_with_tag 并 Base64 编码
    # 格式: [salt(16 bytes) | nonce(12 bytes) | ciphertext_with_tag (variable)]
    encrypted_data = salt + nonce + ciphertext_with_tag
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt_aes_gcm(encrypted_text: str, password: str = config.letsgen_encryption_key) -> str:
    """
    使用 AES-256-GCM 模式解密 Base64 编码的密文。

    参数:
        encrypted_text (str): Base64 编码的加密结果字符串。
        password (str): 用于密钥派生的密码字符串。

    返回:
        str: 解密后的原始字符串。

    抛出:
        cryptography.exceptions.InvalidTag: 如果密文被篡改或密码错误。
        ValueError: 如果密文格式不正确。
    """
    # 1. Base64 解码
    encrypted_data = base64.b64decode(encrypted_text)

    # 2. 验证并分离组件
    SALT_LEN = 16
    NONCE_LEN = 12

    if len(encrypted_data) < SALT_LEN + NONCE_LEN:
        raise ValueError("密文格式错误或长度不足")

    # 分离出 salt, nonce 和 ciphertext (包含认证标签)
    salt = encrypted_data[:SALT_LEN]
    nonce = encrypted_data[SALT_LEN:SALT_LEN + NONCE_LEN]
    ciphertext_with_tag = encrypted_data[SALT_LEN + NONCE_LEN:]

    # 3. 从密码和盐值派生出密钥
    key = _derive_key(password, salt)

    # 4. 创建 AES-GCM 对象
    aes_gcm = AESGCM(key)

    # 5. 执行解密
    # 解密过程会自动验证认证标签。如果标签不匹配（密文被篡改或密钥错误），
    # 则会抛出 InvalidTag 异常。
    decrypted_bytes = aes_gcm.decrypt(
        nonce,
        ciphertext_with_tag,
        associated_data=None
    )

    # 6. 解码为字符串并返回
    return decrypted_bytes.decode('utf-8')


def create_jwt(
    user_name: str,
    role_list: List[str],
    expire_after_minutes: float = config.letsgen_jwt_expire_minutes
) -> str:
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
        algorithm=config.letsgen_jwt_algorithm
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
            algorithms=[config.letsgen_jwt_algorithm],
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
