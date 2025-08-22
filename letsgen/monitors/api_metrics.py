# -*- coding: utf-8 -*-
"""
# @File    : api_metrics.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 22:10
"""

from prometheus_client import Counter

# 测试 metrics api
c = Counter('my_failures', 'Description of counter')
c.inc()  # Increment by 1
c.inc(1.6)  # Increment by given value
