# -*- coding: utf-8 -*-
"""
# @File    : concurrent_log_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 11:42
"""
from letsgen.log.concurrent_log import *


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


async def log_common_file_test():
    # 一般业务日志
    logger = logging.getLogger(__name__)
    # print(logger.handlers)
    # logger.propagate = False

    add_common_file_handler_to_logger(logger)
    add_console_handler_to_logger(logger)
    logger.setLevel(logging.INFO)
    # print(logger.handlers)

    # 异步写入日志
    logger.info("This is an exciting log message!")
    logger.info("Multiple processes can write here concurrently.")
    logger.error("Multiple processes can write here concurrently.")
    logger.warning("warn Multiple processes can write here concurrently.")


def log_data_warehouse_test():
    # 数仓日志
    data_logger = logging.getLogger("data-warehouse")
    add_data_warehouse_handler_to_logger(data_logger)
    add_console_handler_to_logger(data_logger)
    data_logger.setLevel(logging.INFO)
    data_logger.info("This is an exciting data warehouse log message!")

    # 在 console 中配置日志颜色
    # https://blog.csdn.net/Ximerr/article/details/114678389


def log_console_test():
    logger = logging.getLogger(__name__)
    add_console_handler_to_logger(logger)


if __name__ == '__main__':
    # log_common_file_test()

    import asyncio

    asyncio.run(log_common_file_test())
