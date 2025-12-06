# -*- coding: utf-8 -*-
"""
# @File    : util_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 13:28
"""

from letsgen.utils.codec_util import *


def test_padding_to_base64():
    for _ in range(100):
        uuid_b64 = gen_uuid_base64()
        uuid_byte = b64decode(uuid_b64)
        print(uuid_b64, uuid_byte.hex())


def test_phone_number_cipher():
    # 1. 初始化会话加密器
    cipher = PhoneNumberCipher()

    # 2. 原始输入文本：包含两个前后缀相同的冲突手机号
    text1 = (
        "张三的电话是 13911110001，李四的电话是 13922220001。"
        "另外，还有一个号码 17798765432。"
    )

    # 3. 执行加密
    print("\n--- 原始文本 1 ---")
    print(text1)

    encrypted_text1 = cipher.encrypt_text(text1)

    print("\n--- 加密后文本 1 (注意中间的 4 位占位符是不同的非纯数字 Base64 字符) ---")
    print(encrypted_text1)

    print("\n" + "=" * 50)

    # 4. 测试解密功能
    print("--- 待解密文本 (加密后文本 1) ---")
    print(encrypted_text1)

    decrypted_text = cipher.decrypt_text(encrypted_text1)

    print("\n--- 解密后文本 ---")
    print(decrypted_text)

    # 5. 检查解密是否正确
    assert decrypted_text == text1
    print("\n✅ 解密结果校验成功！")

    # 6. 包含大量换行符和分隔的文本
    multiline_text = (
        "联系信息：\n\n"
        "张三 (手机号): 13577778888\n"
        "\n"
        "李四 (旧号，已停用): \n"
        "15000001111\r\n"  # 混合使用 \n 和 \r\n
        "王五 (紧急联系人): 18899990000"
    )

    print("--- 原始多行文本 ---")
    print(multiline_text)

    # 执行加密 (可以直接处理换行符)
    encrypted_text = cipher.encrypt_text(multiline_text)

    print("\n--- 加密后文本 ---")
    print(encrypted_text)

    # 执行解密 (换行符仍然保留)
    decrypted_text = cipher.decrypt_text(encrypted_text)

    print("\n--- 解密后文本 ---")
    print(decrypted_text)

    # 校验：解密后的文本应该与原始文本完全一致
    assert decrypted_text == multiline_text
    print("\n✅ 多行文本处理和校验成功！")
