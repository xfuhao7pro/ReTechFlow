# ReTechFlow API

## 项目背景

ReTechFlow 是面向闲置手机、电脑等二手 3C 产品的智能估价与交易平台。本目录为 Django 后端，提供用户认证、商品发布与审核、图文辅助估价、订单与模拟钱包、在线聊天及交易申诉等功能，使用 MySQL 保存业务数据，Channels 支持 WebSocket 通信。

## 启动方式

准备 Python 3.12、uv 和 MySQL 8，启动 MySQL 并创建数据库。在本目录新建 `mysql.cnf`，填写连接信息：

```ini
[client]
database=retechflow
host=127.0.0.1
port=3306
user=你的数据库用户名
password=你的数据库密码
```

首次配置时将 `.env.example` 复制为 `.env`，填写 AI、邮箱和物流服务配置；已有配置可直接使用。

在项目根目录执行：

```powershell
cd retech-flow-api
uv sync --frozen
uv run python manage.py migrate
uv run daphne -b 127.0.0.1 -p 8000 backend.asgi:application
```

后端地址为 `http://127.0.0.1:8000`，前端需在 `retech-flow-web` 中单独启动。再次运行只需执行最后一条命令，按 `Ctrl+C` 停止服务。`.env` 和 `mysql.cnf` 仅保存在本地。
