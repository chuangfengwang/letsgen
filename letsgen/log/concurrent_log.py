# -*- coding: utf-8 -*-
"""
# @File    : concurrent_log.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-23 16:48
"""
import atexit
import logging
import logging.config
import logging.handlers
import queue
import sys
from typing import Dict, Any

from concurrent_log_handler import ConcurrentTimedRotatingFileHandler

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


def config_common_file_logger_handler(conf: Dict[str, Any]) -> logging.Handler:
    """配置异步多进程安全的日志处理器"""
    # Configure the handler
    rotate_handler = ConcurrentTimedRotatingFileHandler(
        filename=conf["logfile"],
        mode="a",  #
        encoding="utf-8",
        when="D",  # 'D' for daily, 'H' for hourly, 'M' for minute, 'W0'-'W6' for weekly
        interval=1,
        backupCount=15,
        maxBytes=2 * 1024 * 1024 * 1024,  # Optional size-based rotation, 2G
        use_gzip=True
    )
    formatter = logging.Formatter(biz_log_fmt, datefmt=date_fmt)
    rotate_handler.setFormatter(formatter)
    level_only = conf["level_only"]
    rotate_handler.setLevel(level_only)
    rotate_handler.addFilter(OnlyLevelFilter(only_level=level_only))

    if not conf.get("queue_log", False):
        return rotate_handler

    # 异步队列
    log_queue = queue.Queue(maxsize=1000)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    # Set up background processing
    info_queue_listener = logging.handlers.QueueListener(log_queue, rotate_handler)
    info_queue_listener.start()
    atexit.register(info_queue_listener.stop)

    return queue_handler


def config_data_warehouse_file_logger_handler(conf: Dict[str, Any]) -> logging.Handler:
    """配置异步多进程安全的日志处理器"""
    # Configure the handler
    rotate_handler = ConcurrentTimedRotatingFileHandler(
        filename=conf["logfile"],
        mode="a",  #
        encoding="utf-8",
        when="D",  # 'D' for daily, 'H' for hourly, 'M' for minute, 'W0'-'W6' for weekly
        interval=1,
        backupCount=15,
        maxBytes=2 * 1024 * 1024 * 1024,  # Optional size-based rotation, 2G
        use_gzip=True
    )
    formatter = logging.Formatter(fmt=data_log_fmt, datefmt=date_fmt)
    rotate_handler.setFormatter(formatter)
    rotate_handler.setLevel(logging.INFO)

    if not conf.get("queue_log", False):
        return rotate_handler

    # 异步队列
    log_queue = queue.Queue(maxsize=1000)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    # Set up background processing
    info_queue_listener = logging.handlers.QueueListener(log_queue, rotate_handler)
    info_queue_listener.start()
    atexit.register(info_queue_listener.stop)

    return queue_handler


def config_stdout_console_logger_handler(conf) -> logging.Handler:
    """配置标准输出的日志处理器"""
    # stdout_handler 控制台输出 (只显示 INFO)
    stdout_formatter = logging.Formatter(biz_log_fmt, datefmt=date_fmt)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(stdout_formatter)
    handler.addFilter(OnlyLevelFilter(only_level=logging.INFO))
    return handler


def config_stderr_console_logger_handler(conf) -> logging.Handler:
    """配置标准错误的日志处理器"""
    # stderr_handler 控制台输出 (只不显示 INFO)
    stderr_formatter = logging.Formatter(biz_log_fmt, datefmt=date_fmt)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(stderr_formatter)
    handler.addFilter(NotLevelFilter(not_level=logging.INFO))
    return handler


# 一般业务运行日志
info_queue_handler = config_common_file_logger_handler(
    {"logfile": config.info_logfile, "level_only": logging.INFO, "queue_log": True})
warn_queue_handler = config_common_file_logger_handler(
    {"logfile": config.warn_logfile, "level_only": logging.WARN, "queue_log": True})
error_queue_handler = config_common_file_logger_handler(
    {"logfile": config.error_logfile, "level_only": logging.ERROR, "queue_log": True})
# 收集到数仓的日志
data_queue_handler = config_data_warehouse_file_logger_handler(
    {"logfile": config.data_logfile, "queue_log": True})
# console 日志
stdout_handler = config_stdout_console_logger_handler({})
stderr_handler = config_stderr_console_logger_handler({})


def add_common_file_handler_to_logger(logger: logging.Logger):
    """给指定的 logger 添加一般日志 handler"""
    logger.addHandler(info_queue_handler)
    logger.addHandler(warn_queue_handler)
    logger.addHandler(error_queue_handler)


def add_data_warehouse_handler_to_logger(logger: logging.Logger):
    """给指定的 logger 添加数仓日志 handler"""
    logger.addHandler(data_queue_handler)


def add_console_handler_to_logger(logger: logging.Logger):
    """给指定的 logger 添加标准输出/标准错误 handler"""
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)


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
        "letsgen": {  # <--- 使用自定义 Logger 名称
            "handlers": ["stdout_console", "stderr_console", "info_file", "warn_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "data-warehouse": {  # <--- 使用自定义 Logger 名称
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
