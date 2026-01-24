# 发布检查清单

## 📋 第一阶段：准备工作

### 账户准备
- [ ] 有 GitHub 账户（https://github.com）
- [ ] 有 DeepSeek API Key（https://platform.deepseek.com）
- [ ] 可选：有 Railway 账户或计划注册（https://railway.app）

### 本地环境
- [ ] 安装了 Git（https://git-scm.com/download/win）
- [ ] 验证 Git 安装：`git --version` ✅
- [ ] Python 3.9+ 已安装
- [ ] 项目文件完整

### 项目配置检查
- [x] 创建 `.gitignore` - ✅ 已创建
- [x] 创建 `.streamlit/config.toml` - ✅ 已创建
- [x] 创建 `.env.example` - ✅ 已创建
- [x] 创建部署指南 - ✅ 已创建
- [ ] 验证 `requirements.txt` 是否完整
  ```bash
  # 检查是否包含：streamlit, fastapi, uvicorn, sqlalchemy, requests, python-dotenv
  ```

---

## 📋 第二阶段：GitHub 提交

### 本地 Git 配置
- [ ] 进入项目目录：`cd y:\SchneiderProjects\Engineer\sap_query_demo`
- [ ] 初始化 Git：`git init`
- [ ] 配置用户名：`git config --global user.name "Your Name"`
- [ ] 配置邮箱：`git config --global user.email "your.email@example.com"`
- [ ] 验证配置：`git config --global --list`

### 提交代码
- [ ] 暂存文件：`git add .`
- [ ] 验证状态：`git status`
  - ✅ 应该看到所有文件
  - ❌ 不应该看到 `.env`、`*.db`、`__pycache__/`
- [ ] 提交代码：`git commit -m "Initial commit: SAP Query System Demo"`

### GitHub 仓库创建
- [ ] 打开 https://github.com/new
- [ ] 填写仓库信息：
  - 名称：`sap-query-demo`
  - 描述：`SAP Order Query System using Natural Language with Streamlit + FastAPI + DeepSeek LLM`
  - 选择 **Public** 或 **Private**
  - ❌ 不勾选 "Add a README file"
  - ❌ 不勾选 "Add .gitignore"
  - ❌ 不勾选 "Add license"（或可选）
- [ ] 点击 **Create repository**

### 推送到 GitHub
- [ ] 添加远程仓库：`git remote add origin https://github.com/your-username/sap-query-demo.git`
- [ ] 重命名分支：`git branch -M main`
- [ ] 推送代码：`git push -u origin main`
- [ ] 验证成功：访问 `https://github.com/your-username/sap-query-demo`
  - ✅ 所有文件都已上传
  - ✅ `.env` 和 `*.db` 没有上传
  - ✅ README.md 显示正确

---

## 📋 第三阶段：Streamlit Cloud 部署

### 账户准备
- [ ] 访问 https://streamlit.io/cloud
- [ ] 点击 **Sign Up**
- [ ] 使用 GitHub 账户登录授权

### 创建应用
- [ ] 登录 https://share.streamlit.io
- [ ] 点击 **+ New app**
- [ ] 填写应用信息：
  - **Repository**：`your-username/sap-query-demo`
  - **Branch**：`main`
  - **Main file path**：`frontend.py`
- [ ] 点击 **Deploy**
- [ ] 等待 1-2 分钟部署完成

### 配置环境变量
- [ ] 应用部署后，点击右上角 **☰ > Settings**
- [ ] 左侧选择 **Secrets**
- [ ] 粘贴以下内容（替换实际的 API Key）：
  ```
  DEEPSEEK_API_KEY = sk-your-api-key-here
  ```
- [ ] 点击 **Save**
- [ ] 等待应用自动重启（1 分钟）

### 验证部署
- [ ] 应用 URL：`https://your-username-sap-query-demo.streamlit.app`
- [ ] 打开应用链接
- [ ] 检查是否加载正常
- [ ] 尝试登录功能（虽然还无法查询，因为后端未部署）

---

## 📋 第四阶段：Railway 后端部署（可选但推荐）

### Railway 账户准备
- [ ] 访问 https://railway.app
- [ ] 点击 **Login**
- [ ] 使用 GitHub 账户登录

### 部署项目
- [ ] 点击 **+ New** → **GitHub Repo**
- [ ] 授权 GitHub 访问
- [ ] 选择 `sap-query-demo` 仓库
- [ ] 等待部署完成（1-2 分钟）

### 配置环境变量
- [ ] 进入项目 → **Variables**
- [ ] 点击 **+ New Variable**
- [ ] 添加以下变量（替换实际的 API Key）：
  ```
  DEEPSEEK_API_KEY = sk-your-api-key-here
  ```
- [ ] 点击 **Deploy**
- [ ] 等待重新部署完成

### 获取后端 URL
- [ ] 点击 **Settings** → **Domains**
- [ ] 复制显示的 URL（例如：`https://sap-query-demo-prod.up.railway.app`）

### 更新前端配置
- [ ] 本地打开 `frontend.py`
- [ ] 找到第 59 行：`BACKEND_URL = "http://127.0.0.1:8000"`
- [ ] 替换为：`BACKEND_URL = "https://your-railway-url.up.railway.app"`
- [ ] 保存文件

### 推送更新到 GitHub
- [ ] `git add frontend.py`
- [ ] `git commit -m "Update backend URL for cloud deployment"`
- [ ] `git push origin main`
- [ ] 等待 1-2 分钟，Streamlit Cloud 会自动重新部署

### 验证后端连接
- [ ] 打开 Streamlit 应用
- [ ] 尝试登录和查询
- [ ] 验证后端连接正常

---

## ✅ 最终验收清单

### GitHub 仓库
- [ ] 仓库公开或私有，符合您的需求
- [ ] 所有源代码文件已上传
- [ ] `.env` 和 `*.db` 未上传
- [ ] 有清晰的 README.md

### Streamlit Cloud 应用
- [ ] 应用部署成功
- [ ] 应用链接可访问
- [ ] 环境变量已配置
- [ ] 页面加载无错误
- [ ] 登录功能可用

### Railway 后端（可选）
- [ ] 后端部署成功
- [ ] 后端链接可访问
- [ ] 环境变量已配置
- [ ] 前端可以连接到后端
- [ ] 查询功能可用

### 文档完整性
- [x] README.md - 项目说明
- [x] DEPLOYMENT_GUIDE.md - 详细指南
- [x] QUICK_START_DEPLOY.md - 快速步骤
- [x] DEPLOY_SUMMARY.md - 部署摘要
- [x] DEPLOY_FLOW.md - 流程视图
- [x] CHECKLIST.md - 本清单

---

## 🎯 快速参考

### 遇到问题时的检查顺序

1. **应用无法加载**
   - [ ] 检查 Streamlit Cloud 日志（右上角菜单）
   - [ ] 验证 `requirements.txt` 是否完整
   - [ ] 验证 Python 版本是否 3.9+

2. **API Key 错误**
   - [ ] 确认 DEEPSEEK_API_KEY 已在 Secrets 中配置
   - [ ] API Key 格式是否正确（`sk-` 开头）
   - [ ] API Key 是否过期或被禁用

3. **无法连接后端**
   - [ ] 后端是否已部署到 Railway
   - [ ] BACKEND_URL 是否正确
   - [ ] Railway 后端应用是否在运行状态

4. **登录失败**
   - [ ] 检查后端日志
   - [ ] 验证数据库连接
   - [ ] 查看浏览器控制台错误信息

---

## 📞 获取帮助

- 📖 详细步骤：打开 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- ⚡ 快速执行：打开 [QUICK_START_DEPLOY.md](QUICK_START_DEPLOY.md)
- 🎯 流程视图：打开 [DEPLOY_FLOW.md](DEPLOY_FLOW.md)

---

## 💾 保存进度

在您进行部署时，可以在下方记录进度：

```
日期：____________
完成阶段：[ ] 第一阶段 [ ] 第二阶段 [ ] 第三阶段 [ ] 第四阶段
应用 URL：_________________________________________________________
后端 URL：_________________________________________________________
遇到的问题：_____________________________________________________
                  _____________________________________________________
解决方案：_____________________________________________________
```

---

**祝您部署顺利！🚀**

