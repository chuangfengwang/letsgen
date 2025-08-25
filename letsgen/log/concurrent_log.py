# -*- coding: utf-8 -*-
"""
# @File    : concurrent_log.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-23 16:48
"""
import atexit
import logging
import logging.handlers
import queue
import os

from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
import letsgen.config as config

# 配置 basic log
log_fmt = '%(asctime)s.%(msecs)03d - %(name)s:%(lineno)d [%(levelname)s] %(message)s'
data_log_fmt = '%(asctime)s.%(msecs)03d %(levelname)s [%(name)s] %(message)s'
date_fmt = "%Y-%m-%d %H:%M:%S"


# 会为 root logger 生成, <StreamHandler <stderr> (NOTSET)> handler
# logging.basicConfig(
#     level=logging.INFO,
#     format=log_fmt,
#     datefmt=date_fmt
# )

class InfoOnlyFilter(logging.Filter):
    """日志过滤器: 只保留 INFO 级别的日志"""

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


def config_common_logger_handler(logfile: str, level_only: int) -> logging.Handler:
    """配置异步多进程安全的日志处理器"""
    # Configure the handler
    rotate_handler = ConcurrentTimedRotatingFileHandler(
        filename=logfile,
        mode="a",  #
        encoding="utf-8",
        when="D",  # 'D' for daily, 'H' for hourly, 'M' for minute, 'W0'-'W6' for weekly
        interval=1,
        backupCount=15,
        maxBytes=2 * 1024 * 1024 * 1024,  # Optional size-based rotation, 2G
        use_gzip=True
    )
    formatter = logging.Formatter(log_fmt, datefmt=date_fmt)
    rotate_handler.setFormatter(formatter)
    if level_only == logging.INFO:
        rotate_handler.setLevel(logging.INFO)
        rotate_handler.addFilter(InfoOnlyFilter(only_level=logging.INFO))
    elif level_only == logging.WARN:
        rotate_handler.setLevel(logging.WARN)
        rotate_handler.addFilter(InfoOnlyFilter(only_level=logging.WARN))
    elif level_only == logging.ERROR:
        rotate_handler.setLevel(logging.ERROR)
        rotate_handler.addFilter(InfoOnlyFilter(only_level=logging.ERROR))
    # 异步队列
    log_queue = queue.Queue(maxsize=1000)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    # Set up background processing
    info_queue_listener = logging.handlers.QueueListener(log_queue, rotate_handler)
    info_queue_listener.start()
    atexit.register(info_queue_listener.stop)

    return queue_handler


def config_data_warehouse_logger_handler(logfile: str) -> logging.Handler:
    """配置异步多进程安全的日志处理器"""
    # Configure the handler
    rotate_handler = ConcurrentTimedRotatingFileHandler(
        filename=logfile,
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
    # 异步队列
    log_queue = queue.Queue(maxsize=1000)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    # Set up background processing
    info_queue_listener = logging.handlers.QueueListener(log_queue, rotate_handler)
    info_queue_listener.start()
    atexit.register(info_queue_listener.stop)

    return queue_handler


# 一般业务运行日志
info_queue_handler = config_common_logger_handler(config.info_logfile, logging.INFO)
warn_queue_handler = config_common_logger_handler(config.warn_logfile, logging.WARN)
error_queue_handler = config_common_logger_handler(config.error_logfile, logging.ERROR)
# 收集到数仓的日志
data_queue_handler = config_data_warehouse_logger_handler(config.data_logfile)


def add_common_handler_to_logger(logger: logging.Logger):
    """给指定的 logger 添加 handler"""
    logger.addHandler(info_queue_handler)
    logger.addHandler(warn_queue_handler)
    logger.addHandler(error_queue_handler)


def add_data_warehouse_handler_to_logger(logger: logging.Logger):
    """给指定的 logger 添加 handler"""
    logger.addHandler(data_queue_handler)


logger = logging.getLogger()
# print(logger.handlers)

add_common_handler_to_logger(logger)
logger.setLevel(logging.INFO)
# print(logger.handlers)

# 异步写入日志
logger.info("This is an exciting log message!")
logger.info("Multiple processes can write here concurrently.")
logger.error("Multiple processes can write here concurrently.")
logger.warning("warn Multiple processes can write here concurrently.")

data_logger = logging.getLogger("data_warehouse")
add_data_warehouse_handler_to_logger(data_logger)
data_logger.setLevel(logging.INFO)
data_logger.info("This is an exciting data warehouse log message!")

# 在 console 中配置日志颜色
# https://blog.csdn.net/Ximerr/article/details/114678389
