# -*- coding: utf-8 -*-
"""
# @File    : error_class.py
# @Desc    : exceptions
# @Author  : chuangfeng.wang
# @Time    : 2025-10-04 22:14
"""


class LetsgenError(Exception):
    """
    基础异常类
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LlmApiError(LetsgenError):
    """LLM api 基础异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LlmAuthorizationError(LlmApiError):
    """LLM api 鉴权异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LlmParamError(LlmApiError):
    """LLM api 参数不合法异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class LlmRateLimitError(LlmApiError):
    """LLM api 限流异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ProviderError(LetsgenError):
    """LLM 厂商或推理引擎异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ProviderAuthorizationError(ProviderError):
    """LLM 厂商或推理引擎鉴权异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ProviderParamError(ProviderError):
    """LLM 厂商或推理引擎参数异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ProviderRateLimitError(ProviderError):
    """LLM 厂商或推理引擎限流异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ProviderConnectionError(ProviderError):
    """LLM 厂商或推理引擎连接异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ProviderRuntimeError(ProviderError):
    """LLM 厂商或推理引擎执行异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ConfigError(LetsgenError):
    """配置异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class SystemConfigError(ConfigError):
    """系统配置异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class AdminConfigError(ConfigError):
    """管理员后台配置异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UiError(LetsgenError):
    """UI 异常. 消息用于前端提示"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UiAuthorizationError(UiError):
    """UI 鉴权异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UiOpsConfigError(UiError):
    """UI 操作异常"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UiParamError(UiError):
    """UI 参数异常. 消息用于前端提示"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UiParamConflictError(UiParamError):
    """UI 参数冲突异常. 消息用于前端提示"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
