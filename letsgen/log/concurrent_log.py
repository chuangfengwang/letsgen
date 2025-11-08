# -*- coding: utf-8 -*-
"""
# @File    : concurrent_log.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-23 16:48
"""
import logging.handlers

import letsgen.config as config

# 统一配置 log
biz_log_fmt = '%(asctime)s.%(msecs)03d - %(name)s:%(lineno)d [%(levelname)s] %(message)s'
data_log_fmt = '%(asctime)s.%(msecs)03d %(levelname)s [%(name)s] %(message)s'
date_fmt = "%Y-%m-%d %H:%M:%S"


class OnlyLevelFilter(logging.Filter):
    """日志过滤器: 只保留某个级别的日志"""

    def __init__(self, name='', only_level: int = logging.INFO):
        """
        初始化过滤器
        :param name: 过滤器名称
        :param only_level: 日志级别，默认为 INFO
        """
        super().__init__(name)
        self.only_level = only_level

    def filter(self, record: logging.LogRecord):
        # record.levelno 是日志级别的整数值，logging.INFO 是 INFO 级别的整数值
        return record.levelno == self.only_level


class NotLevelFilter(logging.Filter):
    """日志过滤器: 只过滤某个级别的日志"""

    def __init__(self, name='', not_level: int = logging.INFO):
        """
        初始化过滤器
        :param name: 过滤器名称
        :param not_level: 日志级别，默认为 INFO
        """
        super().__init__(name)
        self.only_level = not_level

    def filter(self, record: logging.LogRecord):
        # record.levelno 是日志级别的整数值，logging.INFO 是 INFO 级别的整数值
        return record.levelno != self.only_level


# # 会为 root logger 生成, <StreamHandler <stderr> (NOTSET)> handler
# # 使用 UVICORN_LOGGING_CONFIG 替代
# logging.basicConfig(
#     level=logging.INFO,
#     format=biz_log_fmt,
#     datefmt=date_fmt
# )

# UVICORN 自定义日志配置
UVICORN_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # <--- 关键设置
    "formatters": {
        "biz_log_fmt": {
            "format": biz_log_fmt,
            "datefmt": date_fmt,
        },
        "data_log_fmt": {
            "format": data_log_fmt,
            "datefmt": date_fmt,
        }
    },
    "filters": {
        "info_only": {
            "()": "letsgen.log.concurrent_log.OnlyLevelFilter",
            "only_level": logging.INFO,
        },
        "warn_only": {
            "()": "letsgen.log.concurrent_log.OnlyLevelFilter",
            "only_level": logging.WARNING,
        },
        "error_only": {
            "()": "letsgen.log.concurrent_log.OnlyLevelFilter",
            "only_level": logging.ERROR,
        },
        "info_not": {
            "()": "letsgen.log.concurrent_log.NotLevelFilter",
            "not_level": logging.INFO,
        },
    },
    "handlers": {
        "stdout_console": {
            "class": "logging.StreamHandler",
            "formatter": "biz_log_fmt",
            "level": "INFO",
            'filters': ['info_only'],
            "stream": "ext://sys.stdout",
        },
        "stderr_console": {
            "class": "logging.StreamHandler",
            "formatter": "biz_log_fmt",
            "level": "DEBUG",
            'filters': ['info_not'],
            "stream": "ext://sys.stderr",
        },
        "info_file": {
            "class": "concurrent_log_handler.ConcurrentTimedRotatingFileHandler",
            "formatter": "biz_log_fmt",
            "level": "INFO",
            "filename": config.info_logfile,
            'filters': ['info_only'],
            "mode": "a",  #
            "encoding": "utf-8",
            "when": "D",  # 'D' for daily, 'H' for hourly, 'M' for minute, 'W0'-'W6' for weekly
            "interval": 1,
            "backupCount": 15,
            "maxBytes": 2 * 1024 * 1024 * 1024,  # Optional size-based rotation, 2G
            "use_gzip": True
        },
        "warn_file": {
            "class": "concurrent_log_handler.ConcurrentTimedRotatingFileHandler",
            "formatter": "biz_log_fmt",
            "level": "WARNING",
            "filename": config.warn_logfile,
            'filters': ['warn_only'],
            "mode": "a",  #
            "encoding": "utf-8",
            "when": "D",  # 'D' for daily, 'H' for hourly, 'M' for minute, 'W0'-'W6' for weekly
            "interval": 1,
            "backupCount": 15,
            "maxBytes": 2 * 1024 * 1024 * 1024,  # Optional size-based rotation, 2G
            "use_gzip": True
        },
        "error_file": {
            "class": "concurrent_log_handler.ConcurrentTimedRotatingFileHandler",
            "formatter": "biz_log_fmt",
            "level": "ERROR",
            "filename": config.error_logfile,
            'filters': ['error_only'],
            "mode": "a",  #
            "encoding": "utf-8",
            "when": "D",  # 'D' for daily, 'H' for hourly, 'M' for minute, 'W0'-'W6' for weekly
            "interval": 1,
            "backupCount": 15,
            "maxBytes": 2 * 1024 * 1024 * 1024,  # Optional size-based rotation, 2G
            "use_gzip": True
        },
        "warehouse_file": {
            "class": "concurrent_log_handler.ConcurrentTimedRotatingFileHandler",
            "formatter": "data_log_fmt",
            "level": "INFO",
            "filename": config.data_logfile,
            "mode": "a",  #
            "encoding": "utf-8",
            "when": "D",  # 'D' for daily, 'H' for hourly, 'M' for minute, 'W0'-'W6' for weekly
            "interval": 1,
            "backupCount": 15,
            "maxBytes": 2 * 1024 * 1024 * 1024,  # Optional size-based rotation, 2G
            "use_gzip": True
        },
    },
    "root": {
        "handlers": ["stdout_console", "stderr_console", "info_file", "warn_file", "error_file"],  # 使用您的自定义 Handler
        "level": "INFO",
    },
    "loggers": {
        "letsgen": {  # <--- 使用自定义 Logger 名称, 该项目的 root package
            "handlers": ["stdout_console", "stderr_console", "info_file", "warn_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "data-warehouse": {  # <--- 使用自定义 Logger 名称, 为数仓日志收集准备的日志
            "handlers": ["stdout_console", "stderr_console", "warehouse_file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {  # 确保 Uvicorn 的日志也使用你想要的配置
            "handlers": ["stdout_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
