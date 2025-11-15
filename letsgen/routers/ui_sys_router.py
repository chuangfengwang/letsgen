# -*- coding: utf-8 -*-
"""
# @File    : ui_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 21:25
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse

router = APIRouter(prefix="/api/ui/sys", tags=["sys"])
