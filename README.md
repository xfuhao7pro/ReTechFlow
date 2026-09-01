# ReTechFlow

基于 Django、Vue 和 Channels 的二手 3C 智能估价与交易平台。

## 目录

- `retech-flow-api/`：Django API、WebSocket、订单与估价业务。
- `retech-flow-web/`：Vue 3 前端。
- `二手交易平台需求说明书.md`：当前需求说明。

## 本地运行

后端使用 `uv` 管理 Python 3.12 和依赖，版本以 `pyproject.toml` 与 `uv.lock` 为准。启动时会自动读取本地 `retech-flow-api/.env`；可复制 `.env.example` 创建，真实密钥不要提交。后端依赖 MySQL 和 Redis，数据库连接仍由本地 `retech-flow-api/mysql.cnf` 管理，不提交到 Git。

```powershell
cd .\retech-flow-api
uv sync
uv run python .\manage.py check
uv run daphne -b 127.0.0.1 -p 8000 backend.asgi:application
```

```powershell
cd .\retech-flow-web
npm install
npm run build
npm run dev
```

## 生产部署约束

1. 复制 `.env.example` 的变量到进程管理器或容器环境，不要提交真实密钥。
2. 生产环境必须设置 `DJANGO_DEBUG=False`、`DJANGO_SECRET_KEY`、`DJANGO_ALLOWED_HOSTS`。
3. 生产环境使用 `CHANNEL_LAYER_BACKEND=redis`，保证 WebSocket 在多进程下可用。
4. 前端生产构建必须设置 HTTPS API 地址；未显式指定时，WebSocket 地址会从 API 地址推导为 `wss://`。
5. `ENABLE_MOCK_RECHARGE=False` 时，模拟充值接口不可用。正式支付需要单独接入支付平台和流水表。
