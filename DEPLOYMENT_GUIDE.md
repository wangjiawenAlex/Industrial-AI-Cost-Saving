# GitHub + Streamlit Cloud 完整发布指南

## 📋 目录
1. [准备阶段](#准备阶段)
2. [GitHub 提交](#github-提交)
3. [Streamlit Cloud 发布](#streamlit-cloud-发布)
4. [常见问题](#常见问题)

---

## 准备阶段

### 步骤 1.1：检查项目文件完整性

确保项目包含以下文件：
```
✅ requirements.txt      - 依赖列表
✅ frontend.py          - Streamlit 前端应用（入口）
✅ backend.py           - FastAPI 后端应用
✅ models.py            - 数据库模型
✅ llm_handler.py       - LLM 处理器
✅ sap_mock.py          - SAP 模拟服务
✅ README.md            - 项目说明
✅ .env                 - 环境变量（不上传）
✅ .gitignore           - Git 忽略文件
```

### 步骤 1.2：创建 .streamlit 配置目录

创建 `streamlit/.streamlit/config.toml` 文件（用于Streamlit Cloud配置）：

```bash
# Windows (PowerShell)
mkdir .streamlit
New-Item .streamlit/config.toml -ItemType File

# 或手动创建文件夹和文件
```

### 步骤 1.3：配置 Streamlit 设置文件

编辑 `.streamlit/config.toml`：

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true

[logger]
level = "info"

[server]
maxUploadSize = 200
```

### 步骤 1.4：检查并优化 requirements.txt

当前的 `requirements.txt` 可能需要调整。验证所有依赖：

**关键检查：**
- ✅ 后端依赖（FastAPI, Uvicorn）
- ✅ 前端依赖（Streamlit）
- ✅ 数据库（SQLAlchemy）
- ✅ LLM（Requests, python-dotenv）

**对于 Streamlit Cloud 的建议修改：**

删除特定版本固定，改为最小版本要求（增加兼容性）：

```
streamlit>=1.28.1
fastapi>=0.104.1
uvicorn>=0.24.0
sqlalchemy>=2.0.23
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.5.0
```

### 步骤 1.5：创建 .env.example（示例文件）

创建 `.env.example`（这个文件**会上传**到GitHub，用于告诉用户需要哪些环境变量）：

```bash
# .env.example
DEEPSEEK_API_KEY=sk-your-api-key-here
DATABASE_URL=sqlite:///./sap_query_demo.db
```

---

## GitHub 提交

### 步骤 2.1：安装 Git

**Windows：**
```bash
# 下载安装：https://git-scm.com/download/win
# 或使用 Winget
winget install Git.Git
```

验证安装：
```bash
git --version
```

### 步骤 2.2：配置 Git（首次设置）

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

验证：
```bash
git config --global --list
```

### 步骤 2.3：在项目目录初始化 Git 仓库

```bash
cd y:\SchneiderProjects\Engineer\sap_query_demo
git init
```

### 步骤 2.4：检查 .gitignore

确认 `.gitignore` 文件已创建并包含：
```
.env
*.db
__pycache__/
.venv/
```

### 步骤 2.5：暂存文件（不包括 .env 和数据库）

```bash
# 添加所有文件（除了 .gitignore 中的）
git add .

# 验证暂存的文件（确保 .env 和 *.db 没有被添加）
git status

# 例如输出应该是这样：
# On branch master
# Changes to be committed:
#   new file:   README.md
#   new file:   requirements.txt
#   new file:   frontend.py
#   ... (不应该有 .env 或 sap_query_demo.db)
```

**重要：确保这些文件不在列表中：**
- ❌ `.env`
- ❌ `sap_query_demo.db`
- ❌ `__pycache__/`
- ❌ `.venv/` 或 `venv/`

### 步骤 2.6：初始提交

```bash
git commit -m "Initial commit: SAP Query System Demo

- Streamlit frontend for natural language queries
- FastAPI backend with async support
- SQLAlchemy ORM for database management
- DeepSeek LLM integration for intent recognition
- Complete audit logging system"
```

### 步骤 2.7：在 GitHub 创建仓库

1. 打开 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `sap-query-demo`
   - **Description**: `SAP Order Query System using Natural Language with Streamlit + FastAPI + DeepSeek LLM`
   - **Public** 或 **Private**（推荐 Private，除非想开源）
   - ✅ 勾选 "Add a README file" - **不勾选**（因为已有 README.md）
   - ✅ Add .gitignore - **不勾选**（因为已有 .gitignore）
   - ✅ Add license - **可选**（MIT License 推荐）
3. 点击 "Create repository"

### 步骤 2.8：关联远程仓库并推送

```bash
# 添加远程仓库（将 username 和 repo-name 替换为你的）
git remote add origin https://github.com/your-username/sap-query-demo.git

# 重命名默认分支为 main（GitHub 推荐）
git branch -M main

# 推送代码到 GitHub
git push -u origin main

# 验证推送成功
git log --oneline
```

### 步骤 2.9：验证 GitHub 仓库

访问 `https://github.com/your-username/sap-query-demo` 确认：
- ✅ 所有文件已上传
- ✅ `.env` 和 `*.db` 没有上传
- ✅ README.md 显示正确
- ✅ 提交历史显示

---

## Streamlit Cloud 发布

### 步骤 3.1：创建 Streamlit Cloud 账户

1. 访问 https://streamlit.io/cloud
2. 点击 "Sign Up"
3. 使用 GitHub 账户登录授权（推荐）或邮箱注册

### 步骤 3.2：创建新应用

1. 登录 Streamlit Cloud：https://share.streamlit.io
2. 点击左侧 "Create app" 或 "+ New app"
3. 填写应用信息：
   - **Repository**: 选择 `your-username/sap-query-demo`
   - **Branch**: 选择 `main`
   - **Main file path**: 填写 `frontend.py`
4. 点击 "Deploy"

### 步骤 3.3：配置环境变量

部署后，应用会显示错误（因为缺少 `DEEPSEEK_API_KEY`）：

1. 点击应用右上角三点菜单 → "Settings"
2. 选择左侧 "Secrets"
3. 添加环境变量：
   ```
   DEEPSEEK_API_KEY = sk-your-api-key-here
   ```
4. 点击 "Save"
5. 应用会自动重启

### 步骤 3.4：验证应用部署

应用 URL 为：`https://your-username-sap-query-demo.streamlit.app`

检查：
- ✅ 页面加载正常
- ✅ 登录功能可用
- ✅ 可以输入查询
- ✅ 能连接到后端

### 步骤 3.5：处理后端连接问题

**⚠️ 重要：Streamlit Cloud 上的前端无法直接连接本地后端**

解决方案（二选一）：

#### 方案 A：使用 FastAPI + Streamlit 同时部署

修改 `frontend.py` 启动时同时启动后端：

```python
import subprocess
import time

# 在应用启动时后台启动后端
if not is_backend_running():
    subprocess.Popen(["python", "backend.py"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
    time.sleep(2)  # 等待后端启动
```

#### 方案 B：部署独立的后端服务（推荐）

将后端部署到 Heroku、Railway 或其他云平台：

1. **Railway 部署（推荐，免费）**：
   - 访问 https://railway.app
   - 使用 GitHub 连接
   - 创建新 Project，选择 Python
   - 配置环境变量 `DEEPSEEK_API_KEY`
   - 部署后获得后端 URL，如 `https://xxx.railway.app`

2. **修改 frontend.py 的后端地址**：
   ```python
   BACKEND_URL = "https://your-backend-url.railway.app"  # 改为云端后端
   ```

3. **推送到 GitHub**：
   ```bash
   git add frontend.py
   git commit -m "Update backend URL for cloud deployment"
   git push origin main
   ```

4. **Streamlit Cloud 会自动重新部署**

---

## 常见问题

### Q1：部署后显示 `DEEPSEEK_API_KEY not found`

**原因**：未配置环境变量

**解决**：
1. 进入应用 Settings → Secrets
2. 添加 `DEEPSEEK_API_KEY = sk-xxx`
3. 应用自动重启

### Q2：前端显示 `ConnectionError: unable to connect to http://127.0.0.1:8000`

**原因**：Streamlit Cloud 上的应用无法访问本地后端

**解决**：
- 部署独立的后端服务到云平台（见步骤 3.5 方案 B）
- 更新 BACKEND_URL 配置
- 重新推送代码

### Q3：数据库文件在云上持久化吗？

**原因**：Streamlit Cloud 上的文件系统是临时的，容器重启会丢失数据

**解决**：
- 改用云数据库（PostgreSQL on Heroku/Railway）
- 修改 `DATABASE_URL` 环境变量

```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sap_query_demo.db")
# 云端改为：postgresql://user:pass@host:5432/dbname
```

### Q4：Streamlit Cloud 免费配额是多少？

- ✅ 免费：一个 public app + 1GB 内存 + CPU 共享
- ✅ 推荐：Pro 订阅获得更多资源（$20/月起）

### Q5：如何更新应用？

```bash
# 本地修改代码
# ...修改文件...

# 提交到 GitHub
git add .
git commit -m "Fix: description of changes"
git push origin main

# Streamlit Cloud 会自动重新部署（1-2 分钟）
```

---

## 检查清单

部署前确认以下项都完成：

- [ ] 创建了 `.gitignore`
- [ ] 创建了 `.streamlit/config.toml`
- [ ] 创建了 `.env.example`
- [ ] `requirements.txt` 已更新
- [ ] 本地 Git 已初始化：`git init`
- [ ] 已配置 Git 用户名和邮箱
- [ ] 已暂存并提交代码：`git commit`
- [ ] GitHub 仓库已创建
- [ ] 代码已推送到 GitHub：`git push`
- [ ] Streamlit Cloud 账户已创建
- [ ] 应用已在 Streamlit Cloud 上创建
- [ ] 环境变量 `DEEPSEEK_API_KEY` 已配置
- [ ] 应用成功部署并运行

---

## 后续维护

### 定期更新依赖

```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Upgrade dependencies"
git push origin main
```

### 监控应用性能

- Streamlit Cloud Dashboard：查看应用日志和性能
- GitHub Insights：查看提交历史和协作者

### 保护敏感信息

- ✅ 从不上传 `.env` 文件
- ✅ 使用 Secrets 管理 API Key
- ✅ 数据库密码通过环境变量

