# SAP 订单智能查询系统

> 施耐德电气订单状态智能查询 Demo，基于 FastAPI + Vue3 + DeepSeek LLM

## 📋 项目概述

本系统为施耐德电气提供订单状态智能查询能力。用户可通过自然语言查询订单信息，系统利用 LLM 进行意图识别、从数据库提取订单数据，并生成友好的中文回复。

### 核心能力

- 🔍 **自然语言查询** - 用户输入"查询订单4200000001状态"等自然语言
- 🧠 **意图识别** - DeepSeek LLM 提取订单号和查询意图
- 💾 **数据查询** - 从 PostgreSQL 读取真实订单数据
- ✨ **结果美化** - LLM 生成友好的中文回复
- 📊 **完整日志** - 记录所有查询行为，支持审计追溯

---

## 🏗️ 技术架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue3 前端     │────▶│   FastAPI 后端  │────▶│  PostgreSQL    │
│   (5173/8501)   │     │   (8001)        │     │  (5432)        │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  DeepSeek LLM   │
                        │  (意图识别+美化) │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Redis 缓存    │
                        │   (6379)        │
                        └─────────────────┘
```

### 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Vue3 + Element Plus | 现代 SPA，单页应用 |
| 后端 | FastAPI | Python 异步 Web 框架 |
| 数据库 | PostgreSQL 15 | 关系型数据存储 |
| 缓存 | Redis 7 | LLM 响应缓存 |
| LLM | DeepSeek API | 意图识别 + 结果生成 |
| 认证 | JWT | Token 鉴权 |
| 部署 | Docker Compose | 容器化编排 |

---

## 📁 项目结构

```
Industrial-AI-Cost-Saving/
├── backend.py                  # FastAPI 主应用
├── models.py                   # SQLAlchemy 模型 + JWT 工具
├── llm_handler.py              # DeepSeek LLM 调用封装
├── sap_mock.py                 # 订单数据查询（SQLite 源）
├── migrate_to_postgres.py      # SQLite → PostgreSQL 迁移脚本
├── requirements.txt            # Python 依赖
├── docker-compose.yml          # Docker 编排配置
├── Dockerfile.backend          # 后端镜像
├── Dockerfile.frontend        # 前端镜像
├── .env                        # 环境变量配置
├── frontend-vue/               # Vue3 前端源码
│   ├── src/
│   │   ├── api/               # API 调用
│   │   ├── views/             # 页面组件
│   │   └── router/            # 路由配置
│   └── vite.config.js
└── db/
    └── init/                   # 数据库初始化 SQL
        ├── 01-users.sql
        ├── 02-business_data.sql
        └── 03-query_logs.sql
```

---

## 🚀 快速开始

### 前置条件

- Docker & Docker Compose
- DeepSeek API Key（获取地址：https://platform.deepseek.com）

### 方式一：Docker 一键部署（推荐）

```bash
# 1. 克隆项目
cd /home/wangjiawen/Desktop/saleWeb/Industrial-AI-Cost-Saving

# 2. 配置环境变量（编辑 .env）
vim .env
# 修改 DEEPSEEK_API_KEY 为你的密钥

# 3. 启动全部服务
docker-compose up -d --build

# 4. 检查服务状态
docker-compose ps
```

**访问地址：**
- Vue3 前端：http://localhost:5173
- Streamlit 前端：http://localhost:8501
- 后端 API：http://localhost:8001
- 健康检查：http://localhost:8001/health

### 方式二：本地开发

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 配置环境变量
export DEEPSEEK_API_KEY="sk-xxx"
export DATABASE_URL="postgresql://sap_user:sap_pass123@localhost:5432/sap_db"
export REDIS_URL="redis://localhost:6379/0"

# 3. 初始化数据库
# 确保 PostgreSQL 已启动，运行 db/init/*.sql

# 4. 启动后端
python backend.py
# 后端运行在 http://localhost:8001

# 5. 启动 Vue3 前端（另一个终端）
cd frontend-vue
npm install
npm run dev
# 前端运行在 http://localhost:5173
```

---

## 📡 API 接口

### 认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/login` | POST | 用户登录，返回 JWT Token |

**请求体：**
```json
{
  "username": "demo",
  "password": "demo123"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 订单查询

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/query` | POST | 自然语言订单查询（需认证） |
| `/api/logs` | GET | 查询历史记录（需认证） |
| `/api/user/me` | GET | 获取当前用户信息（需认证） |

**查询请求：**
```json
{
  "query": "查询订单4200000001的状态"
}
```

**查询响应：**
```json
{
  "response": "订单 4200000001 当前状态为制作中，预计完成时间 2024-03-25",
  "order_id": "4200000001",
  "intent": "查询订单状态"
}
```

### 健康检查

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 服务健康状态 |
| `/` | GET | 根路径，返回基本信息 |

---

## 🔐 安全性

| 项目 | 状态 | 说明 |
|------|------|------|
| 密码存储 | ✅ bcrypt | 密码哈希存储，非明文 |
| JWT 认证 | ✅ Token | 60分钟过期 |
| 连接池 | ✅ PostgreSQL | pool_size=10, max_overflow=20 |
| Redis 缓存 | ✅ 已集成 | 减少 LLM 调用 |
| API 限流 | ⚠️ 预留 | 可通过 FastAPI-Limiter 实现 |

---

## 🧪 测试数据

| 订单号 | 客户 | 状态 | 进度 |
|--------|------|------|------|
| 4200000001 | Schneider Electric | 制作中 | 50% |
| 4200000002 | Schneider Electric | 已完成 | 100% |
| 4200000003 | Siemens AG | 已发货 | 100% |

**测试账号：**
- 用户名：`demo`
- 密码：`demo123`

---

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `DEEPSEEK_API_URL` | API 端点 | https://api.deepseek.com/v1 |
| `DEEPSEEK_MODEL` | 模型名称 | deepseek-chat |
| `DATABASE_URL` | PostgreSQL 连接串 | postgresql://sap_user:sap_pass123@postgres:5432/sap_db |
| `REDIS_URL` | Redis 连接串 | redis://redis:6379/0 |
| `JWT_SECRET_KEY` | JWT 密钥 | change-this-in-prod |
| `JWT_EXPIRE_MINUTES` | Token 过期时间 | 60 |
| `FASTAPI_PORT` | 后端端口 | 8000 |

### Docker 端口映射

| 服务 | 容器端口 | 主机端口 |
|------|----------|----------|
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| FastAPI | 8000 | 8001 |
| Vue3 前端 | 5173 | 5173 |
| Streamlit | 8501 | 8501 |

---

## 📝 生产部署注意事项

1. **修改 JWT_SECRET_KEY** - 使用强随机字符串
2. **限制 CORS** - 生产环境设置具体域名
3. **配置 API 限流** - 防止 LLM API 滥用
4. **开启 HTTPS** - 使用 Nginx 反向代理
5. **日志收集** - 接入 Prometheus/Grafana
6. **备份策略** - PostgreSQL 定期备份

---

## 📄 许可证

MIT License

---

## 📞 支持

如有问题请联系：chusilouliu@163.com
