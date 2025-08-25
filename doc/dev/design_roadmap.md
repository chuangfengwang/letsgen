# 功能

接口功能能力
- [ ] openai 兼容接口接入/调用
- [ ] 账号鉴权(bear token)
- [ ] 账号计费
- [ ] 调用限流: rpm/tpm/concurrent
- [ ] 小时级用量统计
- [ ] 调用日志
- [ ] 系统级模型监控
- [ ] 接口转换
- [ ] anthropic 兼容接口接入/调用
- [ ] 为每个厂商配置代理
- [ ] 日志: 分离日志级别, 分离数仓日志


UI 功能
- [ ] 管理员添加新模型/厂商
- [ ] 用户注册/登录/鉴权(jwt)
- [ ] 创建账号/开通模型/充值申请
- [ ] 创建/删除 api-key
- [ ] 管理员审核用户注册/账号创建/模型开通/充值
- [ ] 管理员禁用用户/账号/账号可用的模型
- [ ] 用量看板
- [ ] chat 对话 UI
- [ ] UI 对话记录

# 路径设计安排

根路径重定向到UI首页

UI路径
前缀 /ui
/ui/index.html

UI相关的接口
/api/ui

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
### 基础信息 pg
用户(n)-(n)计费账号(1)-(n)token
账号(1)-(n)钱包, 每个币种一个钱包
账号(n)-(n)模型, 关系表里加: 模态权限, 限流rpm/tpm/concurrent
模型信息表(n)-(n)接入点(n)-(n)接入凭证

apikey 加密存储, 可搜索, 搜索时先加密再搜索

### 日志与统计信息 timescaledb
统计: 小时级每个模型请求数, token数总计, 最大并发
日志: 请求/响应元信息-请求/响应体-对象替代路径


各国法定货币代号 https://www.iban.hk/currency-codes


# 监控
活跃用户数: 做不到
每个模型(流式): 活跃连接数, rpm, tpm, prompt token, completion token, prefix编码速度, 生成速度
每个模型(非流式): 活跃连接数, rpm, tpm, prompt token, completion token, 耗时


# 组件选择
用户权限 jwt

concurrent-log-handler: 解决多 worker 日志冲突问题
uvloop + uvicorn: 替换默认 asyncio 事件循环
gunicorn: 解决多 worker 保活问题

gunicorn 守护的多进程, 及N次请求后重启参数
```bash
gunicorn myapp:app \
-k uvicorn.workers.UvicornWorker \
-w 2 \
--pid /tmp/gunicorn.pid \
--preload \
--graceful-timeout 30 \
--max-requests 10000 \
--max-requests-jitter 1000

kill $(cat /tmp/gunicorn.pid)

gunicorn -c gunicorn_config.py myapp:app


sudo systemctl daemon-reload
sudo systemctl enable gunicorn_letsgen.service
sudo systemctl start gunicorn_letsgen.service
sudo systemctl stop gunicorn_letsgen.service
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

