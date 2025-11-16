# -*- coding: utf-8 -*-
"""
# @File    : password_util_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-19 22:34
"""
from __future__ import annotations

import time

from letsgen.utils.password_util import *


def test_hash_password():
    # 测试哈希和验证功能
    password = "my_secure_password"
    hashed = hash_password(password)
    print("\n")
    assert verify_password(password, hashed) is True
    print("\n")
    assert verify_password("wrong_password", hashed) is False


def test_jwt_functions():
    # 测试 JWT 生成和验证功能
    JWT_SECRET_KEY = "my_jwt_secret"

    # --- 模拟应用鉴权流程 ---

    def protected_api_endpoint(auth_header: str | None):
        """
        模拟一个需要鉴权的 API 接口
        """
        print("\n--- 访问受保护的 API ---")

        if not auth_header:
            print("拒绝访问: 缺少 Authorization Header。")
            return "401 Unauthorized: Missing Token"

        # 1. 从 Authorization Header 中提取 Token
        # 格式通常是 "Bearer <token>"
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                print("拒绝访问: Token 格式错误。")
                return "401 Unauthorized: Invalid Token Scheme"
        except ValueError:
            print("拒绝访问: Token 格式错误。")
            return "401 Unauthorized: Invalid Token Format"

        # 2. 验证 Token
        user_info = verify_jwt(token)

        if user_info:
            # 3. 鉴权成功，处理业务逻辑
            print(f"鉴权成功！用户名: {user_info['user_name']}, role: {user_info['role']}")
            return f"200 OK: 欢迎, {user_info['user_name']}! 这是秘密资源。"
        else:
            # 鉴权失败
            return "401 Unauthorized: Invalid Token"

    # --- 运行示例 ---

    # 1. 模拟用户登录，生成 Token
    print("1. 模拟用户登录，生成 Token...")
    username = "alice"
    role = ["normal"]
    access_token = create_jwt(username, role, 30)
    print(f"生成的 Access Token: {access_token}")

    # 2. 模拟客户端携带 Token 访问 API (成功案例)
    print("\n2. 尝试访问 API (Token 有效)...")
    auth_header_valid = f"Bearer {access_token}"
    response = protected_api_endpoint(auth_header_valid)
    print(f"API 响应: {response}")

    # 3. 模拟 Token 过期访问 (需等待 30 分钟，这里使用一个模拟过期的方法)
    print("\n3. 模拟 Token 过期访问 (人为篡改 exp 字段模拟过期)...")

    # 重新生成一个即时过期的 Token
    now = datetime.datetime.now(datetime.UTC)
    expired_payload = {
        'user_name': username,
        'role': role,
        "iat": now - datetime.timedelta(hours=1),  # 一小时前签发
        "exp": now - datetime.timedelta(minutes=1),  # 一分钟前过期
    }
    expired_token = jwt.encode(expired_payload, config.letsgen_jwt_secret_key, algorithm=config.letsgen_jwt_algorithm)

    auth_header_expired = f"Bearer {expired_token}"
    response_expired = protected_api_endpoint(auth_header_expired)
    print(f"API 响应: {response_expired}")

    # 4. 模拟 Token 被篡改 (改变 Token 的一部分，导致签名验证失败)
    print("\n4. 模拟 Token 被篡改访问...")
    tampered_token = access_token[:-4] + "ABCD"  # 故意修改最后几个字符
    auth_header_tampered = f"Bearer {tampered_token}"
    response_tampered = protected_api_endpoint(auth_header_tampered)
    print(f"API 响应: {response_tampered}")


def test_jwt_expiration():
    # 测试 JWT 过期功能
    username = "test_user"
    role = ["normal"]
    access_token = create_jwt(username, role, 0.1)  # 6秒后过期
    print(f"生成的 Access Token: {access_token}")

    time.sleep(7)  # 等待 7 秒，确保 Token 过期

    user_info = verify_jwt(access_token)
    assert user_info is None
    print("Token 已过期，验证失败。")


def test_encrypt_aes_gcm():
    # ⚠️ 实际应用中请使用更强大的密码
    SECRET_PASSWORD = "MySuperSecretPassword123"
    ORIGINAL_MESSAGE = "这是我的绝密信息，只有我知道密码才能看到。"

    print(f"原始消息: {ORIGINAL_MESSAGE}")
    print(f"使用的密码: {SECRET_PASSWORD}")
    print("-" * 30)

    try:
        # 1. 加密
        encrypted = encrypt_aes_gcm(ORIGINAL_MESSAGE, SECRET_PASSWORD)
        print(f"加密结果 (Base64): {encrypted}")
        print("-" * 30)

        # 2. 解密 (使用正确的密码)
        decrypted = decrypt_aes_gcm(encrypted, SECRET_PASSWORD)
        print(f"解密结果: {decrypted}")
        print("-" * 30)

        # 3. 测试错误密码 (应抛出异常)
        try:
            wrong_password = "WrongPassword"
            print(f"尝试使用错误密码 '{wrong_password}' 解密...")
            decrypt_aes_gcm(encrypted, wrong_password)
        except Exception as e:
            print(f"解密失败，符合预期：{e.__class__.__name__}")

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == '__main__':
    # test_hash_password()
    # test_jwt_functions()
    # test_jwt_expiration()
    test_encrypt_aes_gcm()
