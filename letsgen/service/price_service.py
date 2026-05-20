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
  "unit": "1M-token",  // 计价单位, 通常是 1M-token, 表示每百万token. 国际单位制 (SI) 标准
  "tiers": [  // 分层计价的层级定义
    {
      "range": "[0,200Ki]",  // 输入长度范围. 方括号[]表示闭区间, 圆括号()表示开区间. Ki:1024, Mi:1024*1024. 国际电工委员会 (IEC) 标准
      "input_text":  2.0,  // 输入文本 token 的价格
      "input_image": 2.0,  // 输入图像 token 的价格
      "input_video": 2.0,  // 输入视频 token 的价格
      "input_audio": 2.0,  // 输入音频 token 的价格
      "output_text": 12.0,  // 输出文本 token 的价格
      "output_image": 120.0,  // 输出图像 token 的价格
      "cached": {
        "auto": {  // 隐式缓存计价策略: 即推理引擎自动命中缓存
              "cached_text": 0.5,    // 读取文本缓存 token 的价格
              "cached_image": 0.5,   // 读取图像缓存 token 的价格
              "cached_video": null,  // 不支持这种输入
              "cached_audio": null   // 不支持这种输入
        },
        "declare_ttl": {  // 显式缓存计价策略: 即根据缓存的 ttl 长短分层计价
          "5m":  {   // ttl 设置. 5m 表示 5分钟, 1h 表示 1小时, default 表示系统默认
              "read_text": 0.5,      // 读取文本缓存 token 的价格
              "read_image": 0.5,     // 读取图像缓存 token 的价格
              "read_video": null,    // 不支持这种输入
              "read_audio": null,    // 不支持这种输入
              "write_text": 6.25,    // 写入文本缓存 token 的价格
              "write_image": 6.25,   // 写入图像缓存 token 的价格
              "write_video": null,   // 不支持这种输入
              "write_audio": null    // 不支持这种输入
            },
          "1h": {
            "read_text": 0.5,        // 读取文本缓存 token 的价格
            "read_image": 0.5,       // 读取图像缓存 token 的价格
            "read_video": null,      // 不支持这种输入
            "read_audio": null,      // 不支持这种输入
            "write_text": 10,        // 写入文本缓存 token 的价格
            "write_image": 10,       // 写入图像缓存 token 的价格
            "write_video": null,     // 不支持这种输入
            "write_audio": null      // 不支持这种输入
          }
        }
      }
    },
    {
      "range": "(200Ki,inf)", // 输入长度范围, inf 表示无穷大, 无所谓开闭区间
      "input_text":  8.0,    // 输入文本 token 的价格
      "input_image": 8.0,    // 输入图像 token 的价格
      "input_video": 8.0,    // 输入视频 token 的价格
      "input_audio": 8.0,    // 输入音频 token 的价格
      "output_text": 20.0,   // 输出文本 token 的价格
      "output_image": null,  // 不存在这种情况
      "cached": {
        "auto": {  // 隐式缓存计价策略: 即推理引擎自动命中缓存
              "cached_text": 0.8,   // 读取文本缓存 token 的价格
              "cached_image": 0.8,  // 读取图像缓存 token 的价格
              "cached_video": null,  // 不支持这种输入
              "cached_audio": null  // 不支持这种输入
        },
        "declare_ttl": {  // 显式缓存计价策略: 即根据缓存的 ttl 长短分层计价
          "5m":  {   // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
              "read_text": 0.5,   // 读取文本缓存 token 的价格
              "read_image": 0.5,  // 读取图像缓存 token 的价格
              "read_video": null,  // 不支持这种输入
              "read_audio": null,  // 不支持这种输入
              "write_text": 6.25,   // 写入文本缓存 token 的价格
              "write_image": 6.25,  // 写入图像缓存 token 的价格
              "write_video": null,  // 不支持这种输入
              "write_audio": null  // 不支持这种输入
            },
          "1h": {
            "read_text": 1.0,   // 读取文本缓存 token 的价格
            "read_image": 1.0,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 10,   // 写入文本缓存 token 的价格
            "write_image": 10,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null  // 不支持这种输入
          }
        }
      }
    }
  ]
}

用量表示方式示例:

{
    "completion_tokens": 465,                 // 输出总 token 数
    "prompt_tokens": 9507,                    // 输入总 token 数
    "total_tokens": 9972,                     // 输入输出总 token 数
    "prompt_tokens_details": {
        "audio_tokens": null,                // 输入音频 token 数, 如果不支持音频输入或没有音频输入则为 null
        "cached_tokens": 0,                  // 隐式读取缓存 token 数, 如果没有使用缓存则为 0 或 null. 这部分 token 数包含在 prompt_tokens 中, 但计费单价使用 cached_tokens 的价格
        // 各家在显式缓存上表示不一致, 采用 aliyun 表示法
        // aliyun 与 Anthropic 表示法
        "cache_read_input_tokens": 8959,     // 显式缓存读取总量
        "cache_creation_input_tokens": 248,  // 显式缓存写入总量
        "cache_creation": {                    // 显式写入缓存详情, token 数
            "ephemeral_5m_input_tokens": 248,  // 5m 缓存写入量
            "ephemeral_1h_input_tokens": 0     // 1h 缓存写入量
        }
    },
    "completion_tokens_details": {
        "accepted_prediction_tokens": null,  // 启用 Predicted Outputs 时, 模型接受的预测输出 token 数. 如果没有启用 Predicted Outputs 或没有预测输出则为 null
        "rejected_prediction_tokens": null,  // 启用 Predicted Outputs 时, 模型拒绝的预测输出 token 数. 如果没有启用 Predicted Outputs 或没有预测输出则为 null
        "audio_tokens": null,                // 输出音频 token 数, 如果不支持音频输出或没有音频输出则为 null
        "reasoning_tokens": null,            // 推理 token 数, 仅包含模型推理使用的 token 数. 如果没有推理过程则为 null 或 0
        "text_tokens": 465                   // 输出文本 token 数, 仅包含模型生成的文本输出 token 数. 如果没有文本输出则为 null
    }
}
"""
import math

from typing import NamedTuple, Dict, Any, Optional
from typing import Tuple


class RangeInterval(NamedTuple):
    """带开闭表示的区间范围"""
    left_inclusive: bool
    left_bound: float
    right_bound: float
    right_inclusive: bool


def _parse_token_size(size_str: str) -> float:
    """
    解析大小字符串, 例如 "200Ki" -> 200*1024, "1Mi" -> 1024*1024
    :param size_str: 大小字符串
    :return: 实际大小数值
    """
    size_str = size_str.strip()
    if size_str == "inf":
        return float('inf')
    if size_str == "-inf":
        return float('-inf')

    multipliers = {'Ki': 1024, 'Mi': 1024 * 1024, }
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            return float(size_str[:-2]) * multiplier
    return float(size_str)


def _parse_range(range_str: str) -> RangeInterval:
    """
    解析范围
    :param range_str: 文本表示的范围
    :return: Range 对象
    """
    range_str = range_str.strip()
    left_inclusive = range_str.startswith('[')
    right_inclusive = range_str.endswith(']')

    # 移除括号
    range_str = range_str[1:-1]
    parts = range_str.split(',')
    if len(parts) != 2:
        raise ValueError(f"Invalid RangeInterval str: {range_str}")

    left_bound = _parse_token_size(parts[0].strip())
    right_bound = _parse_token_size(parts[1].strip())

    if math.isinf(left_bound) and left_bound > 0:
        raise ValueError(f"Invalid RangeInterval str: {range_str}")
    if math.isinf(right_bound) and right_bound < 0:
        raise ValueError(f"Invalid RangeInterval str: {range_str}")
    if left_bound > right_bound:
        raise ValueError(f"Invalid RangeInterval str: {range_str}")

    if left_inclusive and math.isinf(left_bound):
        left_inclusive = False
    if right_inclusive and math.isinf(right_bound):
        right_inclusive = False

    return RangeInterval(left_inclusive, left_bound, right_bound, right_inclusive)


def _token_in_range(value: float | int, range_interval: RangeInterval) -> bool:
    """
    判断值是否在指定范围内
    :param value: 待判断的值
    :param range_interval: 范围对象
    :return: 是否在范围内
    """
    if range_interval.left_inclusive:
        left_ok = value >= range_interval.left_bound
    else:
        left_ok = value > range_interval.left_bound

    if range_interval.right_inclusive:
        right_ok = value <= range_interval.right_bound
    else:
        right_ok = value < range_interval.right_bound

    return left_ok and right_ok


def _token_in_range_str(value: float, range_str: RangeInterval) -> bool:
    """
    判断值是否在指定范围内
    :param value: 待判断的值
    :param range_str: 范围字符串, 例如 "[0,200Ki]", "(200Ki,inf)"
    :return: 是否在范围内
    """
    range_interval = _parse_range(range_str)
    return _token_in_range(value, range_interval)


def _find_price_tier(value: float | int, price_tiers: list) -> dict:
    """
    根据值找到对应的价格层级
    :param value: 待查找的值 (例如 prompt_tokens)
    :param price_tiers: 价格层级列表
    :return: 对应的价格层级配置
    """
    for price_tier in price_tiers:
        if _token_in_range_str(value, price_tier['range']):
            return price_tier
    raise ValueError(f"No price_tier found for value: {value}")


def calculate_cost(usage: Dict[str, Any], price_config: Dict[str, Any]) -> Tuple[float, str]:
    """
    根据用量和价格配置计算总费用
    :param usage: 用量数据 (JSON Object)
    :param price_config: 价格配置数据 (JSON Object)
    :return: 总费用 (float) 和 计价单位
    """
    if price_config.get("strategy") != "input-tiered":
        raise ValueError(f"Unsupported strategy: {price_config.get('strategy')}")

    # 1. 确定计价策略的基本单位 (例如 1M-token 代表分母为 1,000,000)
    unit_str = price_config.get("unit", "1M-token")
    if unit_str == "1M-token":
        unit_denominator = 1_000_000.0
    elif unit_str == "1k-token":
        unit_denominator = 1_000.0
    else:
        unit_denominator = 1.0  # 默认为单 token 计价

    # 2. 获取核心用量数据（安全处理 null 值）
    prompt_tokens = usage.get("prompt_tokens", 0) or 0
    completion_tokens = usage.get("completion_tokens", 0) or 0

    prompt_details = usage.get("prompt_tokens_details", {}) or {}
    completion_details = usage.get("completion_tokens_details", {}) or {}

    # 提取各类特殊的输入 Token 数量
    cached_tokens = prompt_details.get("cached_tokens", 0) or 0
    cache_read_tokens = prompt_details.get("cache_read_input_tokens", 0) or 0

    cache_creation_details = prompt_details.get("cache_creation", {}) or {}
    cache_write_5m = cache_creation_details.get("ephemeral_5m_input_tokens", 0) or 0
    cache_write_1h = cache_creation_details.get("ephemeral_1h_input_tokens", 0) or 0

    # 计算标准的、未命中任何缓存的普通输入 Token 数
    # 普通输入 = 总输入 - 隐式缓存 - 显式读取 - 显式写入(5m和1h)
    standard_input_tokens = prompt_tokens - cached_tokens - cache_read_tokens - cache_write_5m - cache_write_1h
    if standard_input_tokens < 0:
        standard_input_tokens = 0  # 兜底防止用量数据统计口径不一致导致负数

    # 3. 匹配对应的分层价格 (Tier)
    matched_tier = _find_price_tier(prompt_tokens, price_config.get("tiers", []))

    # 4. 计算输入（Prompt）相关的费用
    total_cost = 0.0

    # A. 结算普通输入费用 (文本采用 input_text 价格，多模态可根据实际扩展)
    input_price = matched_tier.get("input_text", 0) or 0
    total_cost += (standard_input_tokens / unit_denominator) * input_price

    # B. 结算隐式缓存费用 (auto)
    if cached_tokens > 0:
        auto_cache_price = matched_tier.get("cached", {}).get("auto", {}).get("cached_text", 0) or 0
        total_cost += (cached_tokens / unit_denominator) * auto_cache_price

    # C. 结算显式缓存读取费用 (declare_ttl -> 默认读单价，通常各 ttl 读单价一致，这里取 5m 的 read_text 作为基准)
    if cache_read_tokens > 0:
        read_price = matched_tier.get("cached", {}).get("declare_ttl", {}).get("5m", {}).get("read_text", 0) or 0
        total_cost += (cache_read_tokens / unit_denominator) * read_price

    # D. 结算显式缓存写入费用 (根据不同 TTL 独立计费)
    if cache_write_5m > 0:
        write_5m_price = matched_tier.get("cached", {}).get("declare_ttl", {}).get("5m", {}).get("write_text", 0) or 0
        total_cost += (cache_write_5m / unit_denominator) * write_5m_price

    if cache_write_1h > 0:
        write_1h_price = matched_tier.get("cached", {}).get("declare_ttl", {}).get("1h", {}).get("write_text", 0) or 0
        total_cost += (cache_write_1h / unit_denominator) * write_1h_price

    # 5. 计算输出（Completion）相关的费用
    # 优先计算文本输出，如果未区分，则直接使用 completion_tokens 兜底
    output_text_tokens = completion_details.get("text_tokens", completion_tokens) or completion_tokens
    output_price = matched_tier.get("output_text", 0) or 0

    total_cost += (output_text_tokens / unit_denominator) * output_price

    currency = price_config.get('currency')
    return total_cost, currency
