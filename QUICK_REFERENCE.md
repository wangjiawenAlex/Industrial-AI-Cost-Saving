# 🚀 5 分钟快速参考 - GitHub + Streamlit 部署

> 打印此页面或保存为书签，快速查看部署步骤

---

## 第 1 步：GitHub 提交（5 分钟）

```powershell
# 1. 进入项目目录
cd y:\SchneiderProjects\Engineer\sap_query_demo

# 2. 首次配置 Git（只需一次）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 3. 初始化和提交
git init
git add .
git commit -m "Initial commit: SAP Query System Demo"

# 4. 在 GitHub 创建仓库
# 访问 https://github.com/new
# 仓库名：sap-query-demo
# 创建完成后复制 HTTPS 链接

# 5. 连接并推送
git remote add origin https://github.com/YOUR_USERNAME/sap-query-demo.git
git branch -M main
git push -u origin main
```

✅ **验证**：访问 https://github.com/YOUR_USERNAME/sap-query-demo 看到代码已上传

---

## 第 2 步：Streamlit Cloud 部署（5 分钟）

```
1. 打开 https://share.streamlit.io
2. 点击 "+ New app"
3. 填写：
   - Repository: YOUR_USERNAME/sap-query-demo
   - Branch: main
   - Main file: frontend.py
4. 点击 Deploy（等待 1-2 分钟）
5. 部署完后，点击 ☰ → Settings → Secrets
6. 粘贴：
   DEEPSEEK_API_KEY = sk-your-api-key-here
7. 保存，应用自动重启
```

✅ **验证**：打开应用 URL，看到登录界面

**应用地址**：`https://YOUR_USERNAME-sap-query-demo.streamlit.app`

---

## 第 3 步：Railway 后端部署（可选但推荐）

```
1. 打开 https://railway.app（用 GitHub 登录）
2. 点击 "+ New Project" → "Deploy from GitHub"
3. 选择 sap-query-demo 仓库（授权 GitHub）
4. 等待部署完成（1-2 分钟）
5. 进入项目 → Variables → "+ New Variable"
6. 添加：DEEPSEEK_API_KEY = sk-your-api-key-here
7. 保存，项目重新部署

8. 获取后端 URL：
   点击 Settings → Domains → 复制显示的 URL
   例如：https://sap-query-demo-prod.up.railway.app

9. 更新本地代码：
   打开 frontend.py，找到第 59 行
   改为：BACKEND_URL = "https://sap-query-demo-prod.up.railway.app"

10. 推送更新：
    git add frontend.py
    git commit -m "Update backend URL"
    git push origin main
```

✅ **验证**：Streamlit 应用现在能连接到后端，可以进行查询

---

## ⚡ 命令速查

| 操作 | 命令 |
|------|------|
| 初始化 Git | `git init` |
| 配置用户 | `git config --global user.name "Name"` |
| 检查变更 | `git status` |
| 暂存文件 | `git add .` |
| 提交 | `git commit -m "message"` |
| 添加远程 | `git remote add origin <url>` |
| 重命名分支 | `git branch -M main` |
| 推送 | `git push -u origin main` |
| 后续更新 | `git add .` → `git commit -m "msg"` → `git push` |

---

## 📎 网址收藏

| 用途 | 网址 |
|------|------|
| GitHub 新建仓库 | https://github.com/new |
| GitHub 我的仓库 | https://github.com/your-username/sap-query-demo |
| Streamlit Cloud | https://share.streamlit.io |
| Railway | https://railway.app |
| DeepSeek API | https://platform.deepseek.com |

---

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `fatal: not a git repository` | 未初始化 Git | 运行 `git init` |
| `error: failed to push` | 未设置远程仓库 | 运行 `git remote add origin <url>` |
| `DEEPSEEK_API_KEY not found` | 未配置 Secrets | 在 Streamlit Cloud Settings 添加 |
| `ConnectionError: 127.0.0.1:8000` | 后端未部署到云 | 部署到 Railway 并更新 BACKEND_URL |

---

## ✅ 验收检查

部署完成后检查：

- [ ] GitHub 仓库 https://github.com/your-username/sap-query-demo 可访问
- [ ] Streamlit 应用 https://your-username-sap-query-demo.streamlit.app 可加载
- [ ] 应用显示登录界面，无错误信息
- [ ] 可以输入用户名进行登录
- [ ] （可选）后端部署成功，能进行 SAP 查询

---

## 📞 需要更多信息？

- 详细指南：[QUICK_START_DEPLOY.md](QUICK_START_DEPLOY.md)
- 架构和流程：[DEPLOY_FLOW.md](DEPLOY_FLOW.md)
- 常见问题：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#常见问题)
- 逐步检查：[CHECKLIST.md](CHECKLIST.md)

---

**预计时间**：10-15 分钟 | **难度**：⭐⭐☆☆☆

