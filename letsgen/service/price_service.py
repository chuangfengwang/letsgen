# -*- coding: utf-8 -*-
"""
# @File    : price_service.py
# @Desc    : 计费服务, 当前仅支持按输入token阶梯计费模式
# @Author  : chuangfeng.wang
# @Time    : 2026-02-22 14:07


价格表示方式示例:
{
  "currency": "USD",  // 计价货币单位
  "strategy": "input-tiered",  // 计价策略, 当前仅支持 input-tiered, 即根据输入长度分层计价
  "unit": "1M-token",  // 计价单位, 通常是 1M-token, 表示每百万token
  "tiers": [  // 分层计价的层级定义
    {
      "range": "[0,200k]",  // 输入长度范围. k:1024, m:1024*1024
      "input_text":  2.0,  // 输入文本 token 的价格
      "input_image": 2.0,  // 输入图像 token 的价格
      "input_video": 2.0,  // 输入视频 token 的价格
      "input_audio": 2.0,  // 输入音频 token 的价格
      "output_text": 12.0,  // 输出文本 token 的价格
      "output_image": 120.0,  // 输出图像 token 的价格
      "cached": {
        "strategy": "ttl",  // 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
        "ttl": [
          {
            "range": "(0,5m]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 6.25,   // 写入文本缓存 token 的价格
            "write_image": 6.25,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          },
          {
            "range": "(5m,1h]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 10,   // 写入文本缓存 token 的价格
            "write_image": 10,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          }
        ]
      }
    },
    {
      "range": "(200k,inf)", // 输入长度范围, inf 表示无穷大, 无所谓开闭区间
      "input_text":  4.0,    // 输入文本 token 的价格
      "input_image": 4.0,    // 输入图像 token 的价格
      "input_video": 4.0,    // 输入视频 token 的价格
      "input_audio": 4.0,    // 输入音频 token 的价格
      "output_text": 18.0,   // 输出文本 token 的价格
      "output_image": null,  // 不存在这种情况
      "cached": {
        "strategy": "ttl",  // 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
        "ttl": [
          {
            "range": "(0,5m]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 6.25,   // 写入文本缓存 token 的价格
            "write_image": 6.25,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          },
          {
            "range": "(5m,1h]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 10,   // 写入文本缓存 token 的价格
            "write_image": 10,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          }
        ]
      }
    }
  ]
}

用量表示方式示例:
{
    "completion_tokens": 86,                 // 输出总 token 数
    "prompt_tokens": 64,                     // 输入总 token 数
    "total_tokens": 939,                     // 输入输出总 token 数
    "prompt_tokens_details": {
        "audio_tokens": null,                // 输入音频 token 数, 如果不支持音频输入或没有音频输入则为 null
        "cached_tokens": 0,                  // 读取缓存 token 数, 如果没有使用缓存则为 0 或 null. 这部分 token 数包含在 prompt_tokens 中, 但计费单价使用 cached_tokens 的价格
        "cache_creation_tokens": 0           // 写入缓存 token 数, 如果没有使用缓存则为 0 或 null. 写入缓存的时间根据输入参数确定
    },
    "completion_tokens_details": {
        "accepted_prediction_tokens": null,  // 启用 Predicted Outputs 时, 模型接受的预测输出 token 数. 如果没有启用 Predicted Outputs 或没有预测输出则为 null
        "rejected_prediction_tokens": null,  // 启用 Predicted Outputs 时, 模型拒绝的预测输出 token 数. 如果没有启用 Predicted Outputs 或没有预测输出则为 null
        "audio_tokens": null,                // 输出音频 token 数, 如果不支持音频输出或没有音频输出则为 null
        "reasoning_tokens": null,            // 推理 token 数, 仅包含模型推理使用的 token 数. 如果没有推理过程则为 null
        "text_tokens": 465                   // 输出文本 token 数, 仅包含模型生成的文本输出 token 数. 如果没有文本输出则为 null
    }
}
"""
from typing import Tuple


def _parse_token_size(size_str: str) -> float:
    """
    解析大小字符串, 例如 "200k" -> 200*1024, "1m" -> 1024*1024
    :param size_str: 大小字符串
    :return: 实际大小数值
    """
    size_str = size_str.strip().lower()
    if size_str == "inf":
        return float('inf')

    multipliers = {'k': 1024, 'm': 1024 * 1024, }
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            return float(size_str[:-1]) * multiplier
    return float(size_str)


def _token_in_range(value: float, range_str: str) -> bool:
    """
    判断值是否在指定范围内
    :param value: 待判断的值
    :param range_str: 范围字符串, 例如 "[0,200k]", "(200k,inf)"
    :return: 是否在范围内
    """
    range_str = range_str.strip()
    left_inclusive = range_str.startswith('[')
    right_inclusive = range_str.endswith(']')

    # 移除括号
    range_str = range_str[1:-1]
    parts = range_str.split(',')
    if len(parts) != 2:
        return False

    left_bound = _parse_token_size(parts[0].strip())
    right_bound = _parse_token_size(parts[1].strip())

    if left_inclusive:
        left_ok = value >= left_bound
    else:
        left_ok = value > left_bound

    if right_inclusive:
        right_ok = value <= right_bound
    else:
        right_ok = value < right_bound

    return left_ok and right_ok


def _find_price_tier(value: float, price_tiers: list) -> dict:
    """
    根据值找到对应的价格层级
    :param value: 待查找的值 (例如 prompt_tokens)
    :param price_tiers: 价格层级列表
    :return: 对应的价格层级配置
    """
    for price_tier in price_tiers:
        if _token_in_range(value, price_tier['range']):
            return price_tier
    raise ValueError(f"No price_tier found for value: {value}")


def _parse_time(time_str: str) -> int:
    """
    解析时间字符串, 转换为秒数
    :param time_str: 时间字符串, 例如 "5m" (5分钟), "1h" (1小时)
    :return: 秒数
    """
    time_str = time_str.strip().lower()
    if time_str == "inf":
        return int('inf')

    time_units = {
        's': 1,  # 秒
        'm': 60,  # 分钟
        'h': 3600,  # 小时
        'd': 86400,  # 天
    }

    for suffix, multiplier in time_units.items():
        if time_str.endswith(suffix):
            return int(time_str[:-1]) * multiplier

    # 如果没有单位, 默认按秒处理
    return int(time_str)


def _ttl_in_range(value: float, range_str: str) -> bool:
    """
    判断值是否在指定范围内
    :param value: 待判断的值
    :param range_str: 范围字符串, 例如 "(0,5m]", "(5m,1h]"
    :return: 是否在范围内
    """
    range_str = range_str.strip()
    left_inclusive = range_str.startswith('[')
    right_inclusive = range_str.endswith(']')

    # 移除括号
    range_str = range_str[1:-1]
    parts = range_str.split(',')
    if len(parts) != 2:
        return False

    left_bound = _parse_time(parts[0].strip())
    right_bound = _parse_time(parts[1].strip())

    if left_inclusive:
        left_ok = value >= left_bound
    else:
        left_ok = value > left_bound

    if right_inclusive:
        right_ok = value <= right_bound
    else:
        right_ok = value < right_bound

    return left_ok and right_ok


def _find_ttl_tier(ttl: str, ttl_tiers: list) -> dict:
    """
    根据 TTL 找到对应的缓存价格层级
    :param ttl: TTL 字符串, 例如 "5m", "1h"
    :param ttl_tiers: TTL 层级列表
    :return: 对应的 TTL 层级配置
    """
    if not ttl:
        # 如果没有提供 TTL, 返回第一个层级
        return ttl_tiers[0] if ttl_tiers else {}

    ttl_seconds = _parse_time(ttl)
    for ttl_tier in ttl_tiers:
        if _ttl_in_range(ttl_seconds, ttl_tier['range']):
            return ttl_tier

    # 如果没有找到匹配的层级, 返回第一个层级
    return ttl_tiers[0] if ttl_tiers else {}


def calculate_fee(usage: dict, price_config: dict, cached_ttl: str = None) -> Tuple[float, str]:
    """
    根据用量和价格配置计算本次调用的费用
    :param usage: 用量信息, 包含输入输出 token 数等
    :param price_config: 价格配置信息, 包含计价策略和分层定义
    :param cached_ttl: 如果使用了缓存, 则传入缓存的 TTL 信息, 以便计算缓存相关费用. 取值: None, "5m", "1h" 等
    :return: 本次调用的费用和计价货币单位
    """
    # 获取 token 数量
    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    prompt_details = usage.get('prompt_tokens_details') or {}
    completion_details = usage.get('completion_tokens_details') or {}

    # 提取各类 token 数量
    cached_tokens = prompt_details.get('cached_tokens') or 0
    cache_creation_tokens = prompt_details.get('cache_creation_tokens')
    if not cache_creation_tokens:
        cache_creation_tokens = prompt_details.get('cache_creation', {}).get('cache_creation_input_tokens', 0)
    audio_input_tokens = prompt_details.get('audio_tokens') or 0

    reasoning_tokens = completion_details.get('reasoning_tokens') or 0
    audio_output_tokens = completion_details.get('audio_tokens') or 0
    text_output_tokens = completion_details.get('text_tokens') or completion_tokens - reasoning_tokens

    # 计算非缓存的输入 token (假设都是 text, 除非明确指定是 audio)
    non_cached_input_tokens = prompt_tokens - cached_tokens
    text_input_tokens = non_cached_input_tokens - audio_input_tokens

    # 根据 prompt_tokens 找到对应的价格层级
    tier = _find_price_tier(prompt_tokens, price_config['tiers'])

    # 计价单位, 通常是 1M token
    currency = price_config.get('currency')
    unit = price_config.get('unit', '1M-token')
    if unit == '1M-token':
        unit_divisor = 1_000_000.
    else:
        # 可以根据需要扩展其他单位
        unit_divisor = 1_000_000.

    total_cost = 0.0

    # 计算输入 token 费用 (非缓存部分)
    if text_input_tokens > 0 and tier.get('input_text'):
        total_cost += text_input_tokens * tier['input_text'] / unit_divisor

    if audio_input_tokens > 0 and tier.get('input_audio'):
        total_cost += audio_input_tokens * tier['input_audio'] / unit_divisor

    # 计算输出 token 费用
    if text_output_tokens > 0 and tier.get('output_text'):
        total_cost += text_output_tokens * tier['output_text'] / unit_divisor

    if audio_output_tokens > 0 and tier.get('output_audio'):
        total_cost += audio_output_tokens * tier['output_audio'] / unit_divisor

    # 计算缓存相关费用 (如果有缓存配置)
    cached_config = tier.get('cached')
    if cached_config and (cached_tokens > 0 or cache_creation_tokens > 0):
        if 'ttl' in cached_config:
            ttl_tiers = cached_config['ttl']
            if ttl_tiers:
                # 根据 cached_ttl 参数找到对应的 TTL 层级
                cache_tier = _find_ttl_tier(cached_ttl, ttl_tiers)

                # 读取缓存费用
                # 优先使用 text, 如果有 audio 则计算 audio
                if cached_tokens > 0:
                    read_price = cache_tier.get('read_text')
                    if read_price is not None:
                        total_cost += cached_tokens * read_price / unit_divisor

                # 写入缓存费用
                if cache_creation_tokens > 0:
                    write_price = cache_tier.get('write_text')
                    if write_price is not None:
                        total_cost += cache_creation_tokens * write_price / unit_divisor

    return total_cost, currency
