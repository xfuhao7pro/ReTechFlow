# ReTechFlow

ReTechFlow 是基于 Django 与 Vue 3 的二手 3C 智能估价与交易平台，面向闲置手机、电脑等设备的信息发布与交易需求。系统提供图文辅助估价、商品发布与审核、订单管理、在线聊天、模拟钱包和交易申诉功能。

## 项目结构

- [retech-flow-api](retech-flow-api/README.md)：Django 后端，使用 MySQL 保存数据，Channels 提供即时通信。
- [retech-flow-web](retech-flow-web/README.md)：Vue 3 前端，包含用户页面与平台管理页面。

## 本地启动

准备 Python 3.12、uv、MySQL 8、Node.js 22.12 及以上版本和 npm。先按[后端说明](retech-flow-api/README.md)创建数据库，配置 `mysql.cnf` 与 `.env`，再打开两个终端分别启动：

**后端（从项目根目录执行）**

```powershell
cd retech-flow-api
uv sync --frozen
uv run python manage.py migrate
uv run daphne -b 127.0.0.1 -p 8000 backend.asgi:application
```

**前端（从项目根目录执行）**

```powershell
cd retech-flow-web
npm ci
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

首页：`http://127.0.0.1:5173/home`；管理端：`http://127.0.0.1:5173/admin/login`。

估价、邮件和物流功能需配置相应服务凭据，真实配置仅保存在本地。钱包使用模拟余额，估价结果供用户核对参考。
