# -*- coding: utf-8 -*-
"""
# @File    : concurrent_log_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 11:42
"""
from letsgen.log.concurrent_log import *


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
