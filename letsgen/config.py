# -*- coding: utf-8 -*-
"""
# @File    : config.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:37
"""
import os
import shutil
import sys

from dotenv import load_dotenv

# 确保当前文件所在目录在 sys.path 中
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

# API服务端口
letsgen_web_port = 8000
letsgen_workers = 1
timeout_keep_alive = 5

# 服务工作目录
work_dir = os.path.dirname(os.path.abspath(__file__))

# 日志
logs_dir = os.path.join(work_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)
info_logfile = os.path.join(logs_dir, "info.log")
warn_logfile = os.path.join(logs_dir, "warn.log")
error_logfile = os.path.join(logs_dir, "error.log")
data_logfile = os.path.join(logs_dir, "data-warehouse.log")

# UI 静态文件目录
ui_static_dir = os.path.join(work_dir, "../ui_static")

# prometheus 多进程指标目录
prometheus_metrics_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
if not prometheus_metrics_dir:
    prometheus_metrics_dir = '/tmp/prometheus_metrics'
    os.environ['PROMETHEUS_MULTIPROC_DIR'] = prometheus_metrics_dir
if os.path.exists(prometheus_metrics_dir):
    shutil.rmtree(prometheus_metrics_dir)
os.makedirs(prometheus_metrics_dir, exist_ok=True)

# redis
redis_conn_type = "single"
redis_single_url = os.environ.get("REDIS_SINGLE_URL")

# llm
# 大模型 api 最大等待时间,单位毫秒
llm_api_max_timeout = 600000

# 需要监控 并发/tpm 的路径
letsgen_llm_api = {
    "/api/openai/v1/chat/completion",
    "/api/openai/v1/completions",
}
