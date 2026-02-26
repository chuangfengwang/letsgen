# -*- coding: utf-8 -*-
"""
# @File    : price_service.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2026-02-27 00:03
"""
import json

price = {
    "currency": "USD",  # 计价货币单位
    "strategy": "input-tiered",  # 计价策略, 当前仅支持 input-tiered, 即根据输入长度分层计价
    "unit": "1M-token",  # 计价单位, 通常是 1M-token, 表示每百万token
    "tiers": [  # 分层计价的层级定义
        {
            "range": "[0,200k]",  # 输入长度范围. k:1024, m:1024*1024
            "input_text": 2.0,  # 输入文本 token 的价格
            "input_image": 2.0,  # 输入图像 token 的价格
            "input_video": 2.0,  # 输入视频 token 的价格
            "input_audio": 2.0,  # 输入音频 token 的价格
            "output_text": 12.0,  # 输出文本 token 的价格
            "output_image": 120.0,  # 输出图像 token 的价格
            "cached": {
                "strategy": "ttl",  # 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
                "ttl": [
                    {
                        "range": "(0,5m]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                        "read_text": 0.5,  # 读取文本缓存 token 的价格
                        "read_image": 0.5,  # 读取图像缓存 token 的价格
                        "read_video": None,  # 不支持这种输入
                        "read_audio": None,  # 不支持这种输入
                        "write_text": 6.25,  # 写入文本缓存 token 的价格
                        "write_image": 6.25,  # 写入图像缓存 token 的价格
                        "write_video": None,  # 不支持这种输入
                        "write_audio": None,  # 不支持这种输入
                    },
                    {
                        "range": "(5m,1h]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                        "read_text": 0.5,  # 读取文本缓存 token 的价格
                        "read_image": 0.5,  # 读取图像缓存 token 的价格
                        "read_video": None,  # 不支持这种输入
                        "read_audio": None,  # 不支持这种输入
                        "write_text": 10,  # 写入文本缓存 token 的价格
                        "write_image": 10,  # 写入图像缓存 token 的价格
                        "write_video": None,  # 不支持这种输入
                        "write_audio": None,  # 不支持这种输入
                    }
                ]
            }
        },
        {
            "range": "(200k,inf)",  # 输入长度范围, inf 表示无穷大, 无所谓开闭区间
            "input_text": 4.0,  # 输入文本 token 的价格
            "input_image": 4.0,  # 输入图像 token 的价格
            "input_video": 4.0,  # 输入视频 token 的价格
            "input_audio": 4.0,  # 输入音频 token 的价格
            "output_text": 18.0,  # 输出文本 token 的价格
            "output_image": None,  # 不存在这种情况
            "cached": {
                "strategy": "ttl",  # 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
                "ttl": [
                    {
                        "range": "(0,5m]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                        "read_text": 0.5,  # 读取文本缓存 token 的价格
                        "read_image": 0.5,  # 读取图像缓存 token 的价格
                        "read_video": None,  # 不支持这种输入
                        "read_audio": None,  # 不支持这种输入
                        "write_text": 6.25,  # 写入文本缓存 token 的价格
                        "write_image": 6.25,  # 写入图像缓存 token 的价格
                        "write_video": None,  # 不支持这种输入
                        "write_audio": None,  # 不支持这种输入
                    },
                    {
                        "range": "(5m,1h]",  # ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
                        "read_text": 0.5,  # 读取文本缓存 token 的价格
                        "read_image": 0.5,  # 读取图像缓存 token 的价格
                        "read_video": None,  # 不支持这种输入
                        "read_audio": None,  # 不支持这种输入
                        "write_text": 10,  # 写入文本缓存 token 的价格
                        "write_image": 10,  # 写入图像缓存 token 的价格
                        "write_video": None,  # 不支持这种输入
                        "write_audio": None,  # 不支持这种输入
                    }
                ]
            }
        }
    ]
}
price_info = {"price_info": json.dumps(price, ensure_ascii=False, indent=2)}
print(json.dumps(price_info, ensure_ascii=False, indent=2))
