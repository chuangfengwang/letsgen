# -*- coding: utf-8 -*-
"""
# @File    : log_content_service_test.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-12-08 01:01
"""
from letsgen.service.log_content_service import *

log_content_service = LogContentService()


def test_mime_parse():
    mime_type_list = [
        "text/plain",
        "text/html",
        "application/json",
        "application/xml",
        "image/png",
        "image/jpeg",
        "application/pdf",
        "application/zip",
        "audio/mpeg",
        "video/mp4",
        "application/zip",
        "image/svg+xml",
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # xlsx
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # pptx
    ]
    print()
    for mime_type in mime_type_list:
        extension = log_content_service.parse_mime_file_extension(mime_type)
        object_name = log_content_service.generate_object_name(extension, "I")
        extension = mimetypes.guess_extension(mime_type, strict=True) if mime_type else ''
        print(f"MIME Type: {mime_type} => Object Name: {object_name}. guess_extension: {extension}")
