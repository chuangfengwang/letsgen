# -*- coding: utf-8 -*-
"""
# @File    : config.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:37
"""
import os
import shutil

# API服务端口
letsgen_web_port = 8000
letsgen_workers = 1
timeout_keep_alive = 30

# 服务工作目录
work_dir = os.path.dirname(os.path.abspath(__file__))
# 日志目录
logs_dir = os.path.join(work_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)
# prometheus 多进程指标目录
prometheus_metrics_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
if not prometheus_metrics_dir:
    prometheus_metrics_dir = '/tmp/prometheus_metrics'
    os.environ['PROMETHEUS_MULTIPROC_DIR'] = prometheus_metrics_dir
if os.path.exists(prometheus_metrics_dir):
    shutil.rmtree(prometheus_metrics_dir)
os.makedirs(prometheus_metrics_dir, exist_ok=True)
# UI 静态文件目录
ui_static_dir = os.path.join(work_dir, "../ui_static")
