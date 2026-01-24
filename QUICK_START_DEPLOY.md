# 快速执行步骤 - GitHub + Streamlit Cloud 发布

> ⏱️ 预计时间：10-15 分钟

## 📌 第一部分：GitHub 提交（5 分钟）

### 1️⃣ 初始化 Git 仓库

```powershell
cd y:\SchneiderProjects\Engineer\sap_query_demo
git init
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2️⃣ 暂存并提交文件

```powershell
git add .
git status  # 验证 .env 和 *.db 不在列表中
git commit -m "Initial commit: SAP Query System Demo"
```

### 3️⃣ 在 GitHub 创建仓库

1. 打开 https://github.com/new
2. 仓库名：`sap-query-demo`
3. 选择 **Public** 或 **Private**
4. 点击 **Create repository**（不勾选任何选项）

### 4️⃣ 推送到 GitHub

```powershell
git remote add origin https://github.com/your-username/sap-query-demo.git
git branch -M main
git push -u origin main
```

✅ 完成！代码现在在 GitHub 上了

---

## 📌 第二部分：Streamlit Cloud 发布（5 分钟）

### 1️⃣ 创建 Streamlit Cloud 账户

1. 访问 https://streamlit.io/cloud
2. 点击 **Sign Up**
3. 使用 GitHub 账户授权登录

### 2️⃣ 部署应用

1. 登录 https://share.streamlit.io
2. 点击 **+ New app**
3. 填写：
   - **Repository**: `your-username/sap-query-demo`
   - **Branch**: `main`
   - **Main file path**: `frontend.py`
4. 点击 **Deploy**

⏳ 等待 1-2 分钟...

### 3️⃣ 配置环境变量

部署后看到错误是正常的，需要配置 API Key：

1. 点击右上角 **☰** → **Settings**
2. 左侧选择 **Secrets**
3. 粘贴以下内容到文本框：
   ```
   DEEPSEEK_API_KEY = sk-your-api-key-here
   ```
4. 点击 **Save**

✅ 应用自动重启，应该正常运行了！

---

## 📌 第三部分：后端部署（可选，但推荐）

> **⚠️ 重要**：Streamlit Cloud 前端无法连接本地后端，需要部署独立后端服务

### 使用 Railway 部署后端（免费，推荐）

#### 第 1 步：创建 Railway 账户

1. 访问 https://railway.app
2. 使用 GitHub 账户登录

#### 第 2 步：部署项目

1. 点击 **+ New** → **GitHub Repo**
2. 授权 GitHub 访问
3. 选择 `sap-query-demo` 仓库
4. 等待部署完成（1-2 分钟）

#### 第 3 步：配置环境变量

1. 点击项目 → **Variables**
2. 点击 **+ New Variable**
3. 添加：
   ```
   DEEPSEEK_API_KEY = sk-your-api-key-here
   ```
4. 点击 **Deploy**

#### 第 4 步：获取后端 URL

1. 点击 **Settings** → **Domains**
2. 复制显示的 URL（如 `https://sap-query-demo-prod.up.railway.app`）

#### 第 5 步：更新前端配置

在本地修改 `frontend.py` 的 `BACKEND_URL`：

```python
# 修改第 59 行
BACKEND_URL = "https://sap-query-demo-prod.up.railway.app"  # Railway 后端 URL
```

#### 第 6 步：推送更新到 GitHub

```powershell
git add frontend.py
git commit -m "Update backend URL for cloud deployment"
git push origin main
```

✅ Streamlit Cloud 会自动重新部署，应用现在可以连接到云端后端了！

---

## ✅ 验证清单

- [ ] GitHub 仓库创建成功
- [ ] 代码推送到 GitHub
- [ ] Streamlit Cloud 应用已部署
- [ ] 应用 URL：`https://your-username-sap-query-demo.streamlit.app`
- [ ] 环境变量 `DEEPSEEK_API_KEY` 已配置
- [ ] 应用加载正常（无错误）
- [ ] 可以登录和查询（如果部署了后端）

---

## 📖 更多信息

- 详细指南：见 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Streamlit Cloud 文档：https://docs.streamlit.io/streamlit-cloud
- Railway 文档：https://docs.railway.app

---

## 🆘 常见问题快速解答

### 问题：显示 `DEEPSEEK_API_KEY not found`
**答案**：进入 Streamlit Cloud 应用 Settings → Secrets，添加 API Key

### 问题：前端显示 `ConnectionError: unable to connect to http://127.0.0.1:8000`
**答案**：需要部署后端到云平台（参考第三部分）并更新 BACKEND_URL

### 问题：我想修改代码
**答案**：本地修改 → `git add .` → `git commit` → `git push origin main` → 自动重部署

### 问题：我想撤销上传的文件
**答案**：如果不小心上传了 `.env`，立即执行：
```powershell
git rm --cached .env
git commit -m "Remove .env from git tracking"
git push origin main
git clean -fd  # 删除本地未追踪文件
```

