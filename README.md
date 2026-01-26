# SAP 自然语言查询系统 - Demo

这是一个基于 **Streamlit + FastAPI + DeepSeek API** 的 SAP 订单查询系统 Demo。用户可以通过自然语言查询订单状态，系统会使用 LLM 进行意图识别、SAP 查询和结果美化。

## 📋 项目特点

- ✅ **Streamlit 前端**：快速开发，无需前端工程师
- ✅ **FastAPI 后端**：高性能 API，支持异步处理
- ✅ **DeepSeek LLM**：意图识别和结果美化
- ✅ **数据库日志**：完整的查询审计日志，用于运维追踪
- ✅ **SAP 模拟**：目前硬编码返回"制作中"，便于测试
- ✅ **Docker 支持**：容器化部署，环境一致性

## 🚀 快速开始

### 前置条件

1. **Python 3.9+**
2. **DeepSeek API Key**（获取地址：https://platform.deepseek.com）
3. **Docker & Docker Compose**（可选，用于容器化部署）

### 方式 1：本地运行（推荐用于开发）

#### 步骤 1：克隆或下载项目

```bash
cd /home/ubuntu/sap_query_demo
```

#### 步骤 2：配置环境变量

编辑 `.env` 文件，填入您的 DeepSeek API Key：

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

#### 步骤 3：安装依赖

```bash
pip install -r requirements.txt
```

#### 步骤 4：启动后端服务

在一个终端窗口中运行：

```bash
python backend.py
```

您应该看到类似的输出：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### 步骤 5：启动前端应用

在另一个终端窗口中运行：

```bash
streamlit run frontend.py
```

Streamlit 会自动打开浏览器，显示应用地址：
```
Local URL: http://localhost:8501
Network URL: http://xxx.xxx.xxx.xxx:8501
```

#### 步骤 6：测试应用

1. 在登录页面输入任意用户名和密码（首次登录会自动创建用户）
2. 在查询框中输入自然语言查询，例如：
   - "查询订单 4200000001 的状态"
   - "订单号 4200000002 现在怎么样"
   - "我想知道订单 4200000003 完成了吗"
3. 点击"查询"按钮，系统会返回美化后的结果

### 方式 2：Docker 容器化部署

#### 步骤 1：配置环境变量

编辑 `.env` 文件：

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

#### 步骤 2：启动容器

```bash
docker-compose up -d
```

#### 步骤 3：访问应用

- **前端**：http://localhost:8501
- **后端 API**：http://localhost:8000

#### 步骤 4：查看日志

```bash
# 查看后端日志
docker-compose logs backend

# 查看前端日志
docker-compose logs frontend

# 实时跟踪所有日志
docker-compose logs -f
```

#### 步骤 5：停止容器

```bash
docker-compose down
```

## 📁 项目结构

```
sap_query_demo/
├── backend.py              # FastAPI 后端应用
├── frontend.py             # Streamlit 前端应用
├── models.py               # 数据库模型（用户表、日志表）
├── sap_mock.py             # SAP 模拟模块（硬编码返回"制作中"）
├── llm_handler.py          # LLM 处理模块（意图识别、结果美化）
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile.backend      # 后端 Dockerfile
├── Dockerfile.frontend     # 前端 Dockerfile
└── README.md               # 本文件
```

## 🔄 工作流程

```
用户输入查询
    ↓
Streamlit 前端
    ↓
FastAPI 后端 /api/query
    ↓
LLM 意图识别（提取订单号）
    ↓
SAP 查询（目前硬编码返回"制作中"）
    ↓
LLM 结果美化（组织友好的中文回复）
    ↓
数据库日志记录
    ↓
返回结果给前端
    ↓
用户看到美化后的结果
```

## 📊 数据库表结构

### users 表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| password | VARCHAR(255) | 密码 |
| email | VARCHAR(100) | 邮箱（可选） |
| created_at | DATETIME | 创建时间 |

### query_logs 表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID |
| timestamp | DATETIME | 查询时间 |
| raw_query | TEXT | 用户原始输入 |
| llm_extracted_intent | TEXT | LLM 提取的意图（JSON） |
| sap_raw_response | TEXT | SAP 返回的原始数据（JSON） |
| llm_final_response | TEXT | LLM 美化后的回复 |
| status | VARCHAR(20) | 查询状态（success/error/timeout） |

## 🔐 安全性说明

**当前 Demo 的安全性限制：**

1. **密码存储**：未加密（Demo 模式）。生产环境应使用 bcrypt 或 argon2。
2. **API 认证**：未实现 JWT 或 OAuth。生产环境应添加 Token 认证。
3. **HTTPS**：未启用。生产环境应配置 SSL/TLS。
4. **CORS**：允许所有来源。生产环境应限制来源。

## 🐛 常见问题

### Q1：启动 Streamlit 时出现 "Welcome to Streamlit!" 提示

**A：** 这是 Streamlit 的首次运行提示。您可以：
- 输入邮箱地址，或
- 直接按 Enter 键跳过

然后 Streamlit 会自动打开浏览器。

### Q2：后端无法连接到 DeepSeek API

**A：** 检查以下几点：
1. 确认 `DEEPSEEK_API_KEY` 已正确设置
2. 检查网络连接
3. 确认 API Key 有效且未过期
4. 查看后端日志获取详细错误信息

### Q3：订单号识别失败

**A：** 当前系统期望的订单号格式是 8-10 位数字。您可以：
1. 修改 `sap_mock.py` 中的 `validate_order_id()` 函数
2. 调整 LLM 的提示词以改进识别准确度

### Q4：如何查看查询日志？

**A：** 日志存储在 SQLite 数据库中。您可以：
1. 使用 SQLite 客户端打开 `sap_query_demo.db`
2. 查询 `query_logs` 表
3. 或通过 `/api/logs/{user_id}` API 接口获取

## 📞 支持与反馈

如有问题或建议，请：
1. 检查日志文件
2. 查看 API 文档
3. 联系项目维护者：chusilouliu@163.com

## 📄 许可证

MIT License

---
