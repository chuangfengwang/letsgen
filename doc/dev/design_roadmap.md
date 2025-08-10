# 路径设计安排

根路径重定向到UI首页

UI路径
前缀 /ui
/ui/index.html

UI相关的接口
/api/admin

api文档(自动生成)
/docs

openai系列兼容接口
前缀 /api/openai/
/api/openai/v1/chat/completions

anthropic系列兼容接口
前缀 /api/anthropic
/api/anthropic/v1/messages

# 数据库设计

## DB选择
一般数据DB: postgresql
请求日志(可选): timescaledb
对象存储/对象日志(可选): minio

# 数据表设计
用户(n)-(n)计费账号(1)-(n)token
账号(1)-(n)钱包, 每个币种一个钱包
账号(n)-(n)模型, 关系表里加: 模态权限, 限流rpm/tpm/concurrent
模型信息表(n)-(n)接入点
统计: 小时级每个模型请求数, token数总计, 最大并发
日志: 请求/响应元信息-请求/响应体-对象替代路径

token加密存储, 可搜索, 搜索时先加密再搜索

# 组件选择

concurrent-log-handler: 解决多 worker 日志冲突问题
uvloop + uvicorn: 替换默认 asyncio 事件循环
gunicorn: 解决多 worker 保活问题

gunicorn 守护的多进程, 及N次请求后重启参数
```bash
gunicorn app:app \
-k uvicorn.workers.UvicornWorker \
-w 2 \
--preload \
--max-requests 10000 \
--max-requests-jitter 1000
```


多进程 prometheus client 指标暴露方案
```python
from prometheus_client import multiprocess
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Counter


@app.get("/metrics")
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return Response(content=data, media_type="text/plain")


# 对于 gunicorn, 需要配置中增加
from prometheus_client import multiprocess


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
```


```bash
# export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
```

