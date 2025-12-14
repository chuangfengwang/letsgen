# -*- coding: utf-8 -*-
"""
# @File    : global_service.py
# @Desc    : 全局服务对象, 避开 import 循环引用问题
# @Author  : chuangfeng.wang
# @Time    : 2025-12-14 21:16
"""
from letsgen.service.llm_api_transfer import LlmTransferService

from letsgen.service.log_content_service import LogContentService

# 内容日志记录服务
log_content_service = LogContentService()

from letsgen.service.openai_service import OpenAiChatCompletionsService

# openai chat completions 接口转换服务
llmTransferService: LlmTransferService = OpenAiChatCompletionsService()
