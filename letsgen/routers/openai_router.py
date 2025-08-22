# -*- coding: utf-8 -*-
"""
# @File    : openai_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse

import letsgen.monitors.api_metrics as api_metrics

router = APIRouter(prefix="/api/openai/v1", tags=["openai"])
