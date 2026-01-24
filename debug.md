# SAP 查询系统 - 调试经验总结

## 问题1：后端 login 接口 NameError

### 症状
```
NameError: name 'user' is not defined
```

### 根本原因
在 `backend.py` 的 `login()` 函数（第149行）中，代码直接检查 `if not user:` 但未定义 `user` 变量。缺少了从数据库查询用户的逻辑。

### 修复方案
在第149行之前添加数据库查询语句：
```python
# 从数据库查询用户
user = db.query(User).filter(User.username == request.username).first()

if not user:
    # 如果用户不存在，创建新用户（Demo 模式）
    ...
```

### 关键点
- **登录流程应该是**：先从数据库查询用户 → 如果不存在则创建新用户 → 验证密码
- 这是 Demo 模式，允许自动创建新用户，但前提是要先尝试查询

---

## 问题2：前端 session_state 初始化失败

### 症状
```
KeyError: 'st.session_state has no key "user_id"'
AttributeError: st.session_state has no attribute "user_id"
Session state does not function when running a script without `streamlit run`
```

### 根本原因
用 `python frontend.py` 直接运行 Streamlit 应用，而不是使用 `streamlit run` 命令。Streamlit 的 session_state 功能只在通过 Streamlit 运行时才能正常工作。

### 修复方案
```bash
# ❌ 错误的方式
python frontend.py

# ✅ 正确的方式
streamlit run frontend.py
```

### 关键点
- Streamlit 有特殊的运行方式，需要通过 `streamlit run` 启动应用
- 直接用 Python 运行会绕过 Streamlit 的运行时环境
- session_state、st.rerun() 等高级功能需要 Streamlit 运行时支持

---

## 问题3：后端端口冲突

### 症状
```
[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)
通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

### 根本原因
端口 8000 已被占用，可能是之前的后端进程未正确关闭。

### 修复方案
```bash
# 查看端口占用情况
netstat -ano | findstr 8000

# 杀掉占用进程（根据 PID）
taskkill /PID <PID> /F
```

### 关键点
- Windows 上使用 `netstat -ano | findstr` 查看端口占用
- 使用 `taskkill /PID <PID> /F` 强制杀掉进程
- 确保之前的服务完全关闭再启动新的

---

## 最佳实践

### 启动服务的正确顺序
1. **清理环境**：确保目标端口未被占用
2. **后端启动**：`python backend.py`（后台运行）
3. **前端启动**：`streamlit run frontend.py`（后台运行）
4. **验证**：检查终端输出确认启动成功

### 开发建议
- 使用后台终端运行服务，方便同时观看两个服务的日志
- 后端日志会显示每个 API 请求的详细信息
- 前端访问地址：http://localhost:8502
- 后端 API 文档：http://127.0.0.1:8000/docs

### 常见问题排查
| 问题 | 检查项 |
|------|--------|
| 前端无法连接后端 | 检查后端是否运行，是否使用了正确的端口 8000 |
| Session 状态异常 | 确保使用 `streamlit run` 而非 `python` 启动 |
| 端口冲突 | 使用 `netstat` 检查，用 `taskkill` 清理僵尸进程 |
| 登录失败 | 检查后端日志中的 NameError 或数据库查询异常 |

---

## 文件修改记录

### backend.py
- **修改位置**：第149行前
- **修改内容**：添加用户数据库查询语句
- **目的**：修复 login 函数中 user 变量未定义的问题

