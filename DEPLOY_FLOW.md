# 项目发布流程视图

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    本地开发环境                                   │
│  frontend.py ←→ backend.py                                       │
│  (Streamlit)    (FastAPI)                                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ git push
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub 仓库                                    │
│  sap-query-demo (代码、配置、文档)                               │
└────────┬─────────────────────────────────────────────┬──────────┘
         │                                              │
         │ 自动部署                                     │ 自动部署
         ↓                                              ↓
    Streamlit Cloud                                Railway
    (前端应用)                                    (后端服务)
    ✅ frontend.py                                ✅ backend.py
    https://xxx.streamlit.app                     https://xxx.railway.app
         │                                             │
         └──────────────────→ API Call ←──────────────┘
```

## 时间线

```
第 0 步：准备（已完成）
├─ ✅ 创建 .gitignore
├─ ✅ 创建 .streamlit/config.toml
├─ ✅ 创建 .env.example
├─ ✅ 创建部署指南
└─ ✅ 创建本文件

第 1 步：GitHub 提交（5 分钟）
├─ git init
├─ git config
├─ git add .
├─ git commit
├─ 创建 GitHub 仓库
└─ git push origin main
   ↓
第 2 步：Streamlit Cloud 部署（5 分钟）
├─ 创建 Streamlit Cloud 账户（已有则跳过）
├─ 连接 GitHub 仓库
├─ 部署应用
├─ 添加环境变量（DEEPSEEK_API_KEY）
└─ 应用上线 🎉
   ↓
第 3 步：Railway 后端部署（5 分钟，可选）
├─ 创建 Railway 账户（已有则跳过）
├─ 部署项目
├─ 配置环境变量
├─ 获取后端 URL
├─ 更新 frontend.py
└─ git push origin main
   ↓
完成！应用全面上线 🚀
```

## 命令速查表

### Git 相关

```bash
# 初始化本地仓库
git init

# 配置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 查看变更
git status

# 暂存所有文件
git add .

# 提交
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/username/sap-query-demo.git

# 重命名分支
git branch -M main

# 推送
git push -u origin main

# 后续更新
git add .
git commit -m "Update message"
git push origin main
```

### 网址速查

| 服务 | 网址 |
|------|------|
| GitHub | https://github.com |
| Streamlit Cloud | https://share.streamlit.io |
| Railway | https://railway.app |
| DeepSeek API | https://platform.deepseek.com |
| Git 下载 | https://git-scm.com/download |

## 文件检查清单

### 必需文件（已创建）
- [x] `.gitignore` - Git 忽略配置
- [x] `.streamlit/config.toml` - Streamlit 配置
- [x] `.env.example` - 环境变量模板
- [x] `requirements.txt` - 依赖列表（已存在）
- [x] `README.md` - 项目说明（已存在）

### 部署指南（已创建）
- [x] `DEPLOYMENT_GUIDE.md` - 详细部署指南
- [x] `QUICK_START_DEPLOY.md` - 快速执行步骤
- [x] `DEPLOY_SUMMARY.md` - 部署摘要
- [x] `DEPLOY_FLOW.md` - 本文件（流程视图）

### 不上传文件（自动排除）
- [ ] `.env` - 敏感信息，已在 .gitignore
- [ ] `sap_query_demo.db` - 数据库文件，已在 .gitignore
- [ ] `__pycache__/` - Python 缓存，已在 .gitignore
- [ ] `.venv/` 或 `venv/` - 虚拟环境，已在 .gitignore

## 环境变量配置流程

```
开发环境                 GitHub                    云环境
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  .env 文件   │      │ .env.example │      │  Secrets     │
│  (本地)      │  →   │  (代码库)    │  ←→  │  (云平台)    │
│  私密存储    │      │  示例用途    │      │  安全存储    │
└──────────────┘      └──────────────┘      └──────────────┘
```

**关键点**：
- 开发时：`.env` 文件在本地，不上传到 Git
- 协作时：`.env.example` 告诉团队需要哪些变量
- 云端：使用平台的 Secrets 管理敏感信息

## 应用启动流程（云端）

```
用户访问应用 URL
     ↓
Streamlit Cloud 启动容器
     ↓
运行 frontend.py
     ↓
加载环境变量（从 Secrets）
     ↓
读取 DEEPSEEK_API_KEY
     ↓
读取 BACKEND_URL
     ↓
连接到后端服务
     ↓
应用就绪 ✅
```

## 故障排查流程

```
应用加载失败？
├─ 检查 Streamlit Cloud 日志
├─ DEEPSEEK_API_KEY 是否配置？
├─ requirements.txt 是否有缺失的包？
└─ 代码在本地能运行吗？

无法连接后端？
├─ 后端是否部署到云平台？
├─ BACKEND_URL 是否正确？
├─ 后端是否正常运行？
└─ CORS 是否配置正确？

数据没有保存？
├─ 数据库是本地还是云端？
├─ 如果是云端，容器重启会丢失 SQLite
└─ 建议：迁移到 PostgreSQL
```

## 成本估算

| 服务 | 免费配额 | 推荐方案 |
|------|---------|--------|
| GitHub | 无限 | 免费 ✅ |
| Streamlit Cloud | 1 个 public app | 免费 ✅ |
| Railway | $5/月 | 免费试用 ✅ |
| DeepSeek API | 按 token 计费 | 需付费 |

**总结**：基础部署完全免费，只需支付 API 调用费用

## 下一步行动

1. 👉 **打开** [QUICK_START_DEPLOY.md](QUICK_START_DEPLOY.md)
2. **按步骤** 执行 GitHub 提交
3. **等待** Streamlit Cloud 部署完成
4. **分享** 你的应用链接！

---

**预计总时间**：10-15 分钟 ⏱️

