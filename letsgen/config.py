# -*- coding: utf-8 -*-
"""
# @File    : config.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:37
"""
import os
import shutil

from dotenv import load_dotenv

# 确保当前文件所在目录在 sys.path 中
# import sys
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

# 调试标记
debug_flag = os.environ.get("LETSGEN_DEBUG_FLAG", "false").lower() == "true"

# 服务名称与版本
app_title = "Letsgen Gateway"
app_description = "LLM API Gateway"
app_service_version = "0.1.0"

# API服务端口
letsgen_web_port = 8000
letsgen_workers = 1
timeout_keep_alive = 5

# api doc 配置
expose_api_doc = True if debug_flag else False
use_self_hosted_doc_src = True

# 获取当前脚本目录的父目录, 作为服务工作目录
# cur_dir = os.getcwd()  # 以安装包启动时使用
cur_dir = project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# 日志
logs_dir = os.path.join(cur_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)
info_logfile = os.path.join(logs_dir, "info.log")
warn_logfile = os.path.join(logs_dir, "warn.log")
error_logfile = os.path.join(logs_dir, "error.log")
data_logfile = os.path.join(logs_dir, "data-warehouse.log")

# prometheus 多进程指标目录
prometheus_metrics_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
if not prometheus_metrics_dir:
    prometheus_metrics_dir = '/tmp/letsgen_prometheus_metrics'
if not prometheus_metrics_dir.startswith("/"):
    prometheus_metrics_dir = os.path.join(cur_dir, prometheus_metrics_dir)
if os.path.exists(prometheus_metrics_dir):
    shutil.rmtree(prometheus_metrics_dir)
os.makedirs(prometheus_metrics_dir, exist_ok=True)
os.environ['PROMETHEUS_MULTIPROC_DIR'] = prometheus_metrics_dir

# UI 静态文件目录
fastapi_static_dir = os.path.join(project_dir, "static-fastapi")
ui_static_dir = os.path.join(project_dir, "static-ui")

# redis
redis_conn_type = "single"
redis_single_url = os.environ.get("REDIS_SINGLE_URL")

# pg 基本数据数据库配置
letsgen_db_pg_url = os.environ.get("LETSGEN_DB_PG_URL")
# pg 日志数据库配置
letsgen_log_pg_url = os.environ.get("LETSGEN_LOG_PG_URL")
letsgen_pg_timezone = os.environ.get("LETSGEN_PG_TIMEZONE", "UTC")

# minio
letsgen_minio_endpoint = os.environ.get("LETSGEN_MINIO_ENDPOINT")
letsgen_minio_endpoint_secure = os.environ.get("LETSGEN_MINIO_ENDPOINT_SECURE").lower() != "false"
letsgen_minio_access_key = os.environ.get("LETSGEN_MINIO_ACCESS_KEY")
letsgen_minio_secret_key = os.environ.get("LETSGEN_MINIO_SECRET_KEY")
letsgen_minio_bucket_name = os.environ.get("LETSGEN_MINIO_BUCKET_NAME")
letsgen_minio_public_url = os.environ.get("LETSGEN_MINIO_PUBLIC_URL")
letsgen_minio_internal_url = os.environ.get("LETSGEN_MINIO_INTERNAL_URL")
# S3 对象前缀
letsgen_minio_object_prefix = os.environ.get("LETSGEN_MINIO_OBJECT_PREFIX", "")
# 公网 url 过期时间, 单位: 秒
letsgen_minio_public_expire = int(os.environ.get("LETSGEN_MINIO_PUBLIC_EXPIRE", "86400"))  # 默认 1 天
# 内网 url 过期时间, 单位: 秒
letsgen_minio_internal_expire = int(os.environ.get("LETSGEN_MINIO_INTERNAL_EXPIRE", "315532800"))  # 默认 10 年

# llm
# 大模型 api 最大等待时间,单位毫秒
llm_api_max_timeout = 600000

# 需要监控 并发/tpm/qpm 的路径
letsgen_llm_api = {
    "/api/openai/v1/chat/completions",
}

# 加解密秘钥. 必须是 16/24/32 位字节长度的字符串
letsgen_encryption_key = os.environ.get("LETSGEN_ENCRYPTION_KEY")
if len(letsgen_encryption_key) > 32:
    letsgen_encryption_key = letsgen_encryption_key[:32]
elif len(letsgen_encryption_key) > 24:
    letsgen_encryption_key = letsgen_encryption_key[:24]
elif len(letsgen_encryption_key) > 16:
    letsgen_encryption_key = letsgen_encryption_key[:16]
elif len(letsgen_encryption_key) < 16:
    raise ValueError("LETSGEN_ENCRYPTION_KEY length must be 16, 24, or 32 bytes")
# JWT 秘钥
letsgen_jwt_secret_key = os.environ.get("LETSGEN_JWT_SECRET_KEY")
if not letsgen_jwt_secret_key:
    raise ValueError("LETSGEN_JWT_SECRET_KEY is not set")
letsgen_jwt_algorithm = "HS256"  # JWT 加密算法
letsgen_jwt_expire_minutes = 60 * 24 * 1  # 默认 JWT 过期时间: 1 天

# 默认创建的钱包币种
default_currency_type_list = ["CNY", "USD"]
