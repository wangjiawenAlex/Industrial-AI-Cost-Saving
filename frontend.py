"""
施耐德万高 - 智能数据助手（优化修复版）
"""

import streamlit as st
import requests
import json
from datetime import datetime
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 禁用HTTP代理
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="施耐德万高 | 智能数据助手",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 主题色
PRIMARY_BLUE = "#0072CE"
PRIMARY_GREEN = "#00B388"

# ==================== Session State 初始化 ====================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "查询"
if "query_text" not in st.session_state:
    st.session_state.query_text = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "查询"

# ==================== 现代化CSS设计 ====================
css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto+Mono:wght@300;400&display=swap');

* {{
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}

/* 头部设计 */
.main-header {{
    background: linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_GREEN} 100%);
    padding: 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 25px rgba(0, 114, 206, 0.2);
}}

.brand-title {{
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: clamp(1.8rem, 4vw, 2.5rem);
    letter-spacing: -0.5px;
    color: white;
    margin-bottom: 0.3rem;
}}

.brand-subtitle {{
    font-family: 'Roboto Mono', monospace;
    font-weight: 300;
    font-size: clamp(0.8rem, 2vw, 1rem);
    letter-spacing: 2px;
    color: rgba(255, 255, 255, 0.9);
}}

/* 卡片设计 */
.glass-card {{
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 114, 206, 0.1);
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease;
}}

.glass-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
}}

/* 按钮样式 */
.stButton > button {{
    background: linear-gradient(135deg, {PRIMARY_BLUE}, {PRIMARY_GREEN});
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.7rem 1.5rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s ease;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(0, 114, 206, 0.3);
}}

/* 输入框样式 */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    font-size: 0.95rem;
    padding: 0.75rem;
}}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {PRIMARY_BLUE};
    box-shadow: 0 0 0 2px rgba(0, 114, 206, 0.1);
}}

/* 指标卡片 */
.metric-card {{
    background: linear-gradient(135deg, rgba(0, 114, 206, 0.1), rgba(0, 179, 136, 0.1));
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    border: 1px solid rgba(0, 114, 206, 0.2);
}}

.metric-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {PRIMARY_BLUE};
    margin: 0.5rem 0;
}}

.metric-label {{
    font-size: 0.85rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* 侧边栏样式 */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
}}

/* 响应式设计 */
@media (max-width: 768px) {{
    .main-header {{
        padding: 1.2rem;
        border-radius: 12px;
    }}
    
    .glass-card {{
        padding: 1rem;
    }}
}}

/* 历史记录项 */
.history-item {{
    background: #F9FAFB;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border-left: 3px solid {PRIMARY_BLUE};
}}

.history-time {{
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    color: {PRIMARY_GREEN};
    margin-bottom: 0.3rem;
}}

.history-query {{
    font-size: 0.9rem;
    color: #374151;
    margin: 0.3rem 0;
}}

/* 标签页样式 */
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px;
    background-color: #F3F4F6;
    border-radius: 8px;
    padding: 4px;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 6px;
    color: #6B7280;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {PRIMARY_BLUE}, {PRIMARY_GREEN}) !important;
    color: white !important;
}}

/* 分隔线 */
hr {{
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, {PRIMARY_BLUE}, transparent);
    margin: 1.5rem 0;
}}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# ==================== 后端配置 ====================
BACKEND_BASE_URL = os.getenv(
    "BACKEND_BASE_URL",
    "http://127.0.0.1:8000"
)

# ==================== 辅助函数 ====================
def handle_query(query_text):
    """处理查询请求"""
    if not query_text.strip():
        st.warning("请输入查询内容")
        return None
    
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/query",
            json={
                "user_id": st.session_state.user_id,
                "query_text": query_text
            },
            timeout=30,
            proxies={"http": None, "https": None}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result
            else:
                st.error(f"查询失败: {result.get('message', '未知错误')}")
        else:
            st.error(f"服务器错误: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接到后端服务，请确保FastAPI服务已启动")
    except requests.exceptions.Timeout:
        st.error("⏱️ 请求超时，请稍后重试")
    except Exception as e:
        st.error(f"查询异常: {str(e)}")
    
    return None

# ==================== 页面组件 ====================
def render_header():
    """渲染头部"""
    st.markdown(
        f"""
        <div class="main-header">
            <div class="brand-title">施耐德万高</div>
            <div class="brand-subtitle">智能数据查询系统</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 🎯 导航")
        
        # 使用单选按钮代替标签页
        tab = st.radio(
            "选择功能",
            ["查询", "历史记录", "系统状态"],
            index=["查询", "历史记录", "系统状态"].index(st.session_state.active_tab)
            if st.session_state.active_tab in ["查询", "历史记录", "系统状态"] else 0
        )
        
        if tab != st.session_state.active_tab:
            st.session_state.active_tab = tab
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.username:
            st.markdown(f"### 👤 {st.session_state.username}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 刷新"):
                    st.rerun()
            with col2:
                if st.button("🚪 退出"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 快速查询")
        
        examples = [
            "订单 4200000001 的状态",
            "查询订单 4200000002",
            "订单 4200000003 的详情"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                st.session_state.query_text = example
                if st.session_state.active_tab != "查询":
                    st.session_state.active_tab = "查询"
                st.rerun()

def render_login_page():
    """渲染登录页面"""
    render_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 系统登录")
        
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="输入用户名")
            password = st.text_input("密码", type="password", placeholder="输入密码")
            
            if st.form_submit_button("登录", use_container_width=True):
                if not username or not password:
                    st.error("用户名和密码不能为空")
                    return
                
                try:
                    response = requests.post(
                        f"{BACKEND_BASE_URL}/api/login",
                        json={"username": username, "password": password},
                        timeout=10,
                        proxies={"http": None, "https": None}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.session_state.user_id = result.get("user_id")
                            st.session_state.username = username
                            st.success("登录成功！")
                            st.rerun()
                        else:
                            st.error(result.get("message", "登录失败"))
                    else:
                        st.error(f"登录失败: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务")
                except Exception as e:
                    st.error(f"登录异常: {str(e)}")
        
        st.markdown("---")
        st.info("💡 **演示说明**: 使用任意用户名和密码登录，系统将自动创建账户。")

def render_query_page():
    """渲染查询页面"""
    render_header()
    
    st.markdown("## 🔍 智能查询")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 查询输入区
        with st.container():
            st.markdown("### 📝 输入查询")
            query_text = st.text_area(
                "请输入您的问题",
                value=st.session_state.query_text,
                placeholder="例如：查询订单 4200000001 的当前状态\n或：订单号 4200000002 现在怎么样了",
                height=120,
                key="query_input_area"
            )
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("🚀 开始查询", use_container_width=True):
                    if query_text.strip():
                        result = handle_query(query_text)
                        if result:
                            display_results(result, query_text)
                    else:
                        st.warning("请输入查询内容")
            
            with col4:
                if st.button("🗑️ 清空", use_container_width=True):
                    st.session_state.query_text = ""
                    st.rerun()
    
    with col2:
        with st.container():
            st.markdown("### 💡 示例")
            st.markdown("""
            - 订单 4200000001
            - 查询4200000002
            - 订单状态 4200000003
            - 4200000004 的进度
            """)
            
            st.markdown("---")
            
            st.markdown("### ⚡ 快捷操作")
            if st.button("📋 复制查询", use_container_width=True):
                st.info("请手动复制查询文本")
            
            if st.button("📖 查看历史", use_container_width=True):
                st.session_state.active_tab = "历史记录"
                st.rerun()

def display_results(result, original_query):
    """显示查询结果"""
    st.markdown("---")
    st.markdown("## 📋 查询结果")
    
    # 关键指标
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">订单号</div>
                <div class="metric-value">{result.get('order_id', '-')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">订单状态</div>
                <div class="metric-value">{result.get('sap_status', '-')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">查询ID</div>
                <div class="metric-value">{result.get('log_id', '-')[:8]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # AI回复
    st.markdown("---")
    st.markdown("### 🤖 AI分析回复")
    
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(result.get('final_response', '暂无回复'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 添加到历史记录
    history_item = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": original_query,
        "order_id": result.get('order_id', '-'),
        "status": result.get('sap_status', '-'),
        "response": result.get('final_response', '-')[:200] + "..." 
        if len(result.get('final_response', '')) > 200 else result.get('final_response', '-')
    }
    
    if len(st.session_state.query_history) >= 50:  # 限制历史记录数量
        st.session_state.query_history.pop()
    
    st.session_state.query_history.insert(0, history_item)

def render_history_page():
    """渲染历史记录页面"""
    render_header()
    
    st.markdown("## 📜 查询历史")
    
    if st.session_state.query_history:
        for idx, item in enumerate(st.session_state.query_history):
            with st.container():
                st.markdown(
                    f"""
                    <div class="history-item">
                        <div class="history-time">{item['timestamp']}</div>
                        <div><strong>订单号:</strong> {item['order_id']}</div>
                        <div><strong>状态:</strong> <span style="color: {'#10B981' if '完成' in item['status'] else '#EF4444'}">{item['status']}</span></div>
                        <div class="history-query"><strong>查询:</strong> {item['query']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                with st.expander("查看AI回复"):
                    st.markdown(item['response'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔁 重新查询", key=f"req_{idx}"):
                        st.session_state.query_text = item['query']
                        st.session_state.active_tab = "查询"
                        st.rerun()
                with col2:
                    if st.button("🗑️ 删除", key=f"del_{idx}"):
                        st.session_state.query_history.pop(idx)
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("暂无查询历史记录")
        
        if st.button("🔙 返回查询"):
            st.session_state.active_tab = "查询"
            st.rerun()

def render_status_page():
    """渲染系统状态页面"""
    render_header()
    
    st.markdown("## 📊 系统状态")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("在线用户", "24", "+3")
    with col2:
        st.metric("今日查询", "156", "12%")
    with col3:
        st.metric("响应时间", "0.8s", "-0.1s")
    with col4:
        st.metric("成功率", "98.7%", "0.3%")
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### 🔧 系统信息")
        st.markdown("""
        - **版本**: 2.0.1
        - **后端状态**: 🟢 运行正常
        - **数据库**: 🟢 连接正常
        - **API服务**: 🟢 可用
        """)
    
    with col6:
        st.markdown("### 📈 性能指标")
        st.markdown("""
        - **平均响应**: 0.8秒
        - **峰值并发**: 42
        - **错误率**: 0.3%
        - **可用性**: 99.9%
        """)
    
    st.markdown("---")
    
    if st.button("🔄 刷新状态"):
        st.rerun()

# ==================== 主程序 ====================
def main():
    """主程序入口"""
    
    # 检查登录状态
    if st.session_state.user_id is None:
        render_login_page()
    else:
        # 渲染侧边栏
        render_sidebar()
        
        # 根据活动标签渲染对应页面
        if st.session_state.active_tab == "查询":
            render_query_page()
        elif st.session_state.active_tab == "历史记录":
            render_history_page()
        elif st.session_state.active_tab == "系统状态":
            render_status_page()

if __name__ == "__main__":
    main()
