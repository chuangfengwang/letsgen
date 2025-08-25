# -*- coding: utf-8 -*-
"""
# @File    : api_metrics.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 22:10
"""

from prometheus_client import Counter, Gauge, Summary


# 接口 qps
api_in_qps = Counter("letsgen_api_in", "api入口计数", ["path", "model", "interact_mode"])
api_success_qps = Counter('letsgen_api_success', 'api成功计数', ["path", "model", "interact_mode"])
api_fail_qps = Counter('letsgen_api_fail', 'api失败计数', ["path", "model", "interact_mode"])

# 接口延时
api_e2e_latency = Summary('letsgen_api_e2e_latency', 'api端到端延时', ["path", "provider", "model", "interact_mode"])
provider_e2e_latency = Summary('letsgen_provider_e2e_latency', '厂端到端商延时', ["path", "provider", "model", "interact_mode"])
provider_1st_token_latency = Summary('letsgen_provider_1st_token_latency', 'api调用厂商延时', ["path", "provider", "model"])

# token 数
all_token = Counter('letsgen_all_token', '输入输出token总数', ["path", "model", "interact_mode"])
prompt_token = Counter('letsgen_prompt_token', '输入token总数', ["path", "model", "interact_mode"])
completion_token = Counter('letsgen_completion_token', '输出token总数', ["path", "model", "interact_mode"])
cache_token = Counter('letsgen_cache_token', '缓存token总数', ["path", "model", "interact_mode"])
reason_token = Counter('letsgen_reason_token', '推理token总数', ["path", "model", "interact_mode"])

# 接口并发
api_concurrent = Gauge('letsgen_api_concurrent', 'api入口并发计数', ["path", "model", "interact_mode"])
provider_concurrent = Gauge('letsgen_provider_concurrent', '厂商并发计数', ["path", "model", "interact_mode"])
