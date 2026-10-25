# ReTechFlow Web

## 项目背景

ReTechFlow 为闲置手机、电脑等二手 3C 产品提供信息发布、辅助估价和交易服务。本目录为 Vue 3 前端，包含首页、交易广场、估价、订单、聊天和个人中心，以及商品审核、申诉处理等后台管理页面。

前端使用 TypeScript、Vite、Element Plus、Vue Router 和 Pinia，通过 HTTP 与 WebSocket 连接后端。

## 启动方式

准备 Node.js 22.12 及以上版本和 npm，并先启动后端。首次配置时将 `.env.example` 复制为 `.env`，默认连接 `http://127.0.0.1:8000`；后端地址变化时同步修改 `VITE_API_BASE_URL` 和 `VITE_WS_BASE_URL`。

在项目根目录执行：

```powershell
cd retech-flow-web
npm ci
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

首页：`http://127.0.0.1:5173/home`；管理端：`http://127.0.0.1:5173/admin/login`。

日常开发执行上述最后一条命令即可。`npm run build` 完成类型检查并生成 `dist/`，`npm run preview` 可预览构建结果；按 `Ctrl+C` 停止服务。
