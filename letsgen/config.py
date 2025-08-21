#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @File    : config.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-08-21 20:37
"""
import os

# API服务端口
letsgen_web_port = 8000
letsgen_workers = 1
timeout_keep_alive = 30

# 服务工作目录
work_dir = os.path.dirname(os.path.abspath(__file__))
# 日志目录
logs_dir = os.path.join(work_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)
# UI 静态文件目录
ui_static_dir = os.path.join(work_dir, "../ui_static")
