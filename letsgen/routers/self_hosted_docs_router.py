# -*- coding: utf-8 -*-
"""
# @File    : self_hosted_docs_router.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-11-15 21:55
"""
import fastapi_cdn_host
from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

import config


def set_self_host_docs(app: FastAPI):
    """设置自托管 docs 静态资源"""

    # 自定义 docs 地址
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            # swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_js_url="/static/swagger-ui-dist@5/swagger-ui-bundle.js",
            # swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
            swagger_css_url="/static/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    # 自定义 redoc 地址
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            # redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
            redoc_js_url="/static/swagger-ui-dist@5/redoc.standalone.js",
        )

    # fastapi_cdn_host.patch_docs(app)
    app.mount("/static", StaticFiles(directory=config.fastapi_static_dir), name="fastapi-static")
