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
