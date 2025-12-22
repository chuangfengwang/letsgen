# 生产环境部署指南

## 问题说明

Vite 的代理配置（`server.proxy`）**仅在开发环境有效**，在生产环境构建后（`npm run build`）不起作用。

## 解决方案

生产环境有两种常见的部署方案：

### 方案一：使用 Nginx 反向代理（推荐）

这是最常见的生产环境部署方案，前后端部署在同一域名下，通过 Nginx 代理 API 请求。

#### 1. 构建前端项目

```bash
npm run build
```

构建产物在 `dist` 目录。

#### 2. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location /ui/ {
        alias /path/to/your/dist/;
        try_files $uri $uri/ /ui/index.html;
        index index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS 头（如果需要）
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
        
        # 处理预检请求
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS';
            add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }

    # 根路径重定向到 /ui/
    location = / {
        return 301 /ui/;
    }
}
```

#### 3. 环境变量配置

确保 `.env.production` 文件中的配置为：

```env
VITE_API_BASE_URL=/api/ui
```

这样前端会使用相对路径，请求会被 Nginx 代理到后端。

---

### 方案二：后端配置 CORS（前后端分离部署）

如果前后端部署在不同的域名/端口，需要在后端配置 CORS 头。

#### 1. 环境变量配置

修改 `.env.production` 文件：

```env
VITE_API_BASE_URL=https://api.your-domain.com/api/ui
```

#### 2. 后端需要添加的 CORS 头

后端服务器需要返回以下响应头：

```
Access-Control-Allow-Origin: https://your-frontend-domain.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

#### 3. 处理预检请求（OPTIONS）

后端需要正确处理 OPTIONS 预检请求，返回 200 状态码和相应的 CORS 头。

---

## 环境变量说明

- **开发环境** (`.env.development`): 使用完整 URL，通过 Vite 代理转发
- **生产环境** (`.env.production`): 
  - 方案一（Nginx 代理）: 使用相对路径 `/api/ui`
  - 方案二（CORS）: 使用完整 URL `https://api.your-domain.com/api/ui`

## 验证

部署后，打开浏览器开发者工具，检查：
1. 网络请求是否成功
2. 响应头中是否包含正确的 CORS 头（如果使用方案二）
3. 控制台是否有 CORS 错误

