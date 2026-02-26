# Docker 化前后端开发方案（FastAPI + Streamlit + PostgreSQL + DeepSeek 企业级 API）

## 1. 目标与原则

本方案目标：

1. 在 **Docker 环境**中实现前后端并行开发（本地热更新）。
2. 明确前后端服务拆分与 API 对接方式。
3. 用 **PostgreSQL** 模拟 3 张核心表：
   - `users`（用户表）
   - `business_data`（业务数据表，订单/主数据模拟）
   - `query_logs`（查询日志表，新增日志审计）
4. LLM 侧统一接入 **DeepSeek 企业级 API**（可切换私有网关/API Base URL）。

---

## 2. 目标架构

```text
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                      │
│                                                         │
│   ┌──────────────┐    HTTP     ┌──────────────────┐    │
│   │   frontend   │ ─────────▶  │     backend      │    │
│   │  Streamlit   │             │ FastAPI + SQLA   │    │
│   └──────────────┘             └────────┬─────────┘    │
│                                          │              │
│                              SQL         │ HTTPS        │
│                                          ▼              │
│                                 ┌──────────────┐       │
│                                 │  postgres    │       │
│                                 │   (3 tables) │       │
│                                 └──────────────┘       │
│                                          │              │
└──────────────────────────────────────────┼──────────────┘
                                           │
                                           ▼
                                  DeepSeek Enterprise API
```

---

## 3. 容器与职责

### 3.1 frontend（Streamlit）
- 负责 UI 登录、自然语言输入、结果展示、历史查看。
- 不直接访问数据库；仅调用 backend API。
- 通过环境变量 `BACKEND_BASE_URL=http://backend:8000` 对接后端。

### 3.2 backend（FastAPI）
- 对外提供认证、查询、日志 API。
- 持有业务编排逻辑：
  1) 调 DeepSeek 提取意图（订单号）；
  2) 查 `business_data` 模拟业务返回；
  3) 调 DeepSeek 美化结果；
  4) 落库 `query_logs`。
- 持有数据库连接池与 ORM（SQLAlchemy）。

### 3.3 postgres
- 仅负责存储与查询。
- 挂载初始化脚本自动建库建表（`docker-entrypoint-initdb.d/*.sql`）。
- 开发环境暴露 `5432` 方便本地工具连库。

---

## 4. PostgreSQL 三张表设计

> 你提出“用户表 + 数据表 + log表”，这里建议如下：

## 4.1 users（用户表）
```sql
CREATE TABLE IF NOT EXISTS users (
  id              BIGSERIAL PRIMARY KEY,
  username        VARCHAR(50) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  email           VARCHAR(100) UNIQUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

## 4.2 business_data（业务数据表，模拟订单）
```sql
CREATE TABLE IF NOT EXISTS business_data (
  id                    BIGSERIAL PRIMARY KEY,
  order_id              VARCHAR(20) UNIQUE NOT NULL,
  customer_name         VARCHAR(100),
  status                VARCHAR(30) NOT NULL,
  status_code           VARCHAR(10),
  progress_percentage   INT CHECK (progress_percentage BETWEEN 0 AND 100),
  details               TEXT,
  expected_completion   TIMESTAMPTZ,
  last_update           TIMESTAMPTZ DEFAULT NOW(),
  created_at            TIMESTAMPTZ DEFAULT NOW()
);
```

## 4.3 query_logs（查询日志表，新增）
```sql
CREATE TABLE IF NOT EXISTS query_logs (
  id                    BIGSERIAL PRIMARY KEY,
  user_id               BIGINT NOT NULL REFERENCES users(id),
  order_id              VARCHAR(20),
  raw_query             TEXT NOT NULL,
  llm_extracted_intent  JSONB,
  business_raw_response JSONB,
  llm_final_response    TEXT,
  status                VARCHAR(20) NOT NULL DEFAULT 'success',
  error_message         TEXT,
  trace_id              VARCHAR(64),
  latency_ms            INT,
  created_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_query_logs_user_id_created_at
ON query_logs(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_query_logs_order_id
ON query_logs(order_id);
```

---

## 5. API 设计与前后端连接

## 5.1 认证
- `POST /api/login`
  - 入参：`username`, `password`
  - 逻辑：用户不存在则注册（开发阶段），存在则校验密码（生产改为 JWT）
  - 出参：`success`, `user_id`, `message`

## 5.2 订单查询
- `POST /api/query`
  - 入参：`user_id`, `query_text`
  - 后端流程：
    1. DeepSeek 提取 `order_id`
    2. `SELECT * FROM business_data WHERE order_id = :order_id`
    3. DeepSeek 美化回复
    4. 记录 `query_logs`
  - 出参：`order_id`, `status`, `final_response`, `log_id`

## 5.3 历史日志
- `GET /api/logs/{user_id}`
  - 用于前端“查询历史”展示
  - 可分页（`page`, `page_size`）

---

## 6. DeepSeek 企业级 API 接入规范

## 6.1 环境变量
```bash
DEEPSEEK_API_KEY=your_enterprise_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

> 如企业走专线/网关，将 `DEEPSEEK_API_URL` 指向企业网关地址即可，不改业务代码。

## 6.2 后端调用建议
- 统一封装 `LLMClient`（超时、重试、熔断、日志脱敏）。
- 设置 `request timeout`（例如 10s）和 `max retries`（例如 2 次指数退避）。
- 记录 `trace_id` 到 `query_logs` 便于排障。
- 不在日志中落明文 API Key。

---

## 7. docker-compose（开发模式）

建议新增 `docker-compose.dev.yml`：

```yaml
version: "3.9"
services:
  postgres:
    image: postgres:16
    container_name: iacs-postgres
    environment:
      POSTGRES_DB: sap_demo
      POSTGRES_USER: sap_user
      POSTGRES_PASSWORD: sap_pass
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sap_user -d sap_demo"]
      interval: 5s
      timeout: 3s
      retries: 10

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: iacs-backend
    environment:
      DATABASE_URL: postgresql+psycopg2://sap_user:sap_pass@postgres:5432/sap_demo
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      DEEPSEEK_API_URL: ${DEEPSEEK_API_URL:-https://api.deepseek.com/v1}
      DEEPSEEK_MODEL: ${DEEPSEEK_MODEL:-deepseek-chat}
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    working_dir: /app
    command: uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: iacs-frontend
    environment:
      BACKEND_BASE_URL: http://backend:8000
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    working_dir: /app
    command: streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0
    depends_on:
      - backend

volumes:
  pgdata:
```

---

## 8. 目录建议

```text
.
├── backend.py
├── frontend.py
├── llm_handler.py
├── models.py
├── db/
│   └── init/
│       ├── 001_schema.sql
│       └── 002_seed_business_data.sql
├── docker-compose.dev.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── .env
```

---

## 9. 开发启动步骤（团队统一）

1. 复制环境变量：
```bash
cp .env.example .env
```
2. 在 `.env` 填写 DeepSeek 企业 Key。
3. 启动：
```bash
docker compose -f docker-compose.dev.yml up -d --build
```
4. 验证：
- 前端：http://localhost:8501
- 后端健康检查：http://localhost:8000/health
- 数据库：localhost:5432

5. 查看日志：
```bash
docker compose -f docker-compose.dev.yml logs -f backend
```

---

## 10. 与当前代码衔接改造清单（最小改造）

1. `models.py`：SQLite 改为 PostgreSQL URL（保留 env 注入）。
2. `User.password` 改名 `password_hash`（登录逻辑改为哈希校验）。
3. 新增 `BusinessData` ORM 对应 `business_data`。
4. `sap_mock.py` 替换为 `business_data` 查询函数（保留 mock fallback）。
5. `QueryLog` 增加 `trace_id`、`latency_ms`、`error_message` 字段。
6. `llm_handler.py` 使用 `DEEPSEEK_MODEL` 环境变量，统一重试策略。

---

## 11. 里程碑建议

- **M1（1-2天）**：Docker 三服务跑通 + PG 三表初始化 + 健康检查。
- **M2（2-3天）**：后端改造接 PG + 业务数据查询替代 mock。
- **M3（1-2天）**：DeepSeek 企业 API 稳定性增强（超时、重试、trace）。
- **M4（1天）**：前端联调、历史查询分页、错误提示优化。

---

## 12. 风险与建议

1. **API 波动风险**：建议添加重试、降级模板回复。
2. **日志合规风险**：日志里避免记录敏感字段明文。
3. **并发增长风险**：后续可在 backend 前加 Nginx，并为 PostgreSQL 增加连接池参数。
4. **生产安全**：CORS 白名单、JWT、密码哈希、HTTPS 必须纳入正式需求。

