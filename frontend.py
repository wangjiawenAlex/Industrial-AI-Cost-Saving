"""
施耐德万高 - 智能数据助手（科技感重制版）
现代化响应式设计，增强科技感与交互体验
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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com',
        'Report a bug': "https://www.example.com",
        'About': "施耐德万高智能数据查询系统 demo"
    }
)

# 主题色（科技感配色）
PRIMARY_BLUE = "#0072CE"
PRIMARY_GREEN = "#00B388"
DARK_BLUE = "#0A1A2F"
LIGHT_BLUE = "#E3F2FD"
ACCENT_PURPLE = "#7B61FF"
GRADIENT_START = "#0072CE"
GRADIENT_END = "#00B388"

# ==================== 现代化CSS设计 ====================
css = f"""
<style>
/* 导入现代化字体 */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto+Mono:wght@300;400&display=swap');

:root {{
    --primary-blue: {PRIMARY_BLUE};
    --primary-green: {PRIMARY_GREEN};
    --dark-blue: {DARK_BLUE};
    --light-blue: {LIGHT_BLUE};
    --accent-purple: {ACCENT_PURPLE};
    --gradient-start: {GRADIENT_START};
    --gradient-end: {GRADIENT_END};
    --glass-bg: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.2);
}}

* {{
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #0A1A2F 0%, #1E3A5F 100%);
    color: #FFFFFF;
    min-height: 100vh;
}}

/* 科技感头部设计 */
.main-header {{
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 114, 206, 0.3);
}}

.main-header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}}

.brand-title {{
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: clamp(2rem, 5vw, 3rem);
    letter-spacing: -0.5px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    position: relative;
    margin-bottom: 0.5rem;
}}

.brand-subtitle {{
    font-family: 'Roboto Mono', monospace;
    font-weight: 300;
    font-size: clamp(0.9rem, 2vw, 1.1rem);
    letter-spacing: 3px;
    opacity: 0.9;
    position: relative;
}}

/* 玻璃态卡片设计 */
.glass-card {{
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.glass-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}}

/* 现代化按钮 */
.stButton > button {{
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 114, 206, 0.3);
    position: relative;
    overflow: hidden;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 114, 206, 0.4);
}}

.stButton > button:active {{
    transform: translateY(0);
}}

.stButton > button::after {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: 0.5s;
}}

.stButton > button:hover::after {{
    left: 100%;
}}

/* 输入框美化 */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    color: white;
    font-size: 1rem;
    padding: 0.8rem 1rem;
}}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 2px rgba(0, 114, 206, 0.2);
}}

/* 指标卡片 */
.metric-card {{
    background: linear-gradient(135deg, rgba(0, 114, 206, 0.15), rgba(0, 179, 136, 0.15));
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid rgba(0, 114, 206, 0.3);
}}

.metric-value {{
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #0072CE, #00B388);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0.5rem 0;
}}

.metric-label {{
    font-size: 0.9rem;
    color: #A0AEC0;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* 标签页样式 */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 4px;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent;
    border-radius: 8px;
    color: #A0AEC0;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
    color: white !important;
}}

/* 响应式设计 */
@media (max-width: 768px) {{
    .main-header {{
        padding: 1.5rem;
        border-radius: 16px;
    }}
    
    .brand-title {{
        font-size: 1.8rem;
    }}
    
    .glass-card {{
        padding: 1rem;
    }}
}}

/* 加载动画 */
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

.loading-pulse {{
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}}

/* 自定义滚动条 */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb {{
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: linear-gradient(135deg, var(--primary-blue), var(--primary-green));
}}

/* 数据表格美化 */
.dataframe {{
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}}

/* 通知样式 */
.stAlert {{
    border-radius: 12px !important;
    border: none !important;
    backdrop-filter: blur(10px);
}}

/* 登录页面特殊样式 */
.login-container {{
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
}}

.login-card {{
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}}

.login-title {{
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #FFFFFF, #A0AEC0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.login-subtitle {{
    color: #A0AEC0;
    margin-bottom: 2rem;
}}

/* 历史记录样式 */
.history-item {{
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid var(--primary-blue);
    transition: all 0.3s ease;
}}

.history-item:hover {{
    background: rgba(255, 255, 255, 0.08);
    transform: translateX(5px);
}}

.history-time {{
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: var(--primary-green);
}}

.history-query {{
    font-size: 0.95rem;
    margin: 0.3rem 0;
}}

/* 打字机效果 */
@keyframes typing {{
    from {{ width: 0 }}
    to {{ width: 100% }}
}}

@keyframes blink-caret {{
    from, to {{ border-color: transparent }}
    50% {{ border-color: var(--primary-green) }}
}}

.typing-effect {{
    overflow: hidden;
    white-space: nowrap;
    margin: 0 auto;
    letter-spacing: 0.15em;
    animation: 
        typing 3.5s steps(40, end),
        blink-caret 0.75s step-end infinite;
}}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# ==================== 后端配置 ====================
BACKEND_BASE_URL = os.getenv(
    "BACKEND_BASE_URL",
    "http://127.0.0.1:8000"
)

# ==================== Session State 管理 ====================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "查询"

# ==================== 公共组件 ====================

def render_header():
    """渲染现代化头部"""
    st.markdown(
        f"""
        <div class="main-header">
            <div class="brand-title">SCHNEIDER VACON</div>
            <div class="brand-subtitle">INTELLIGENT DATA ASSISTANT</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem;">施耐德万高</div>
                <div style="font-size: 0.9rem; color: #A0AEC0; margin-bottom: 2rem;">智能数据查询系统</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 导航菜单
        st.markdown("### 📊 导航")
        tabs = st.radio(
            "选择功能",
            ["查询", "历史", "仪表板", "设置"],
            label_visibility="collapsed"
        )
        st.session_state.current_tab = tabs
        
        st.markdown("---")
        
        # 用户信息
        if st.session_state.username:
            st.markdown(f"### 👤 {st.session_state.username}")
            if st.button("🚪 退出登录", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.query_history = []
                st.rerun()
        
        # 系统状态
        st.markdown("### 📈 系统状态")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("在线用户", "24", "+3")
        with col2:
            st.metric("今日查询", "156", "12%")
        
        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 0.8rem; color: #718096; text-align: center;">
                施耐德万高 
            </div>
            """,
            unsafe_allow_html=True
        )

def render_login_page():
    """渲染现代化登录页面"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div class="login-container">
                <div class="login-card">
                    <h2 class="login-title">欢迎回来</h2>
                    <p class="login-subtitle">登录您的账户继续使用</p>
            """,
            unsafe_allow_html=True
        )
        
        # 登录表单
        with st.form("login_form"):
            username = st.text_input(
                "用户名",
                placeholder="输入用户名",
                help="请输入您的用户名"
            )
            
            password = st.text_input(
                "密码",
                type="password",
                placeholder="输入密码",
                help="请输入您的密码"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                remember = st.checkbox("记住我")
            with col2:
                st.markdown(
                    '<a href="#" style="color: var(--primary-blue); text-decoration: none;">忘记密码？</a>',
                    unsafe_allow_html=True
                )
            
            submit_button = st.form_submit_button(
                "🔐 登录",
                use_container_width=True
            )
            
            if submit_button:
                if not username or not password:
                    st.error("请填写用户名和密码")
                    return
                
                with st.spinner("正在验证身份..."):
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
                    except Exception as e:
                        st.error(f"连接错误: {str(e)}")
        
        st.markdown(
            """
            <div style="margin-top: 2rem; text-align: center; color: #718096; font-size: 0.9rem;">
                <p>演示账户: 任意用户名/密码</p>
                <p style="margin-top: 0.5rem;">首次登录将自动创建账户</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_query_page():
    """渲染查询页面"""
    render_header()
    
    st.markdown(
        """
        <h2 style="margin-bottom: 0.5rem;">🔍 智能查询</h2>
        <p style="color: #A0AEC0; margin-bottom: 2rem;">使用自然语言查询您的订单数据</p>
        """,
        unsafe_allow_html=True
    )
    
    # 主查询区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            # 查询输入
            query_text = st.text_area(
                "📝 输入您的查询",
                placeholder="例如：查询订单 4200000001 的当前状态\n或：我想知道订单号 4200000002 的详细信息",
                height=120,
                key="query_input"
            )
            
            col3, col4 = st.columns([1, 3])
            with col3:
                if st.button(
                    "🚀 开始查询",
                    use_container_width=True,
                    disabled=not query_text.strip()
                ):
                    # 处理查询逻辑
                    handle_query(query_text)
            
            with col4:
                st.markdown(
                    """
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <span style="font-size: 0.9rem; color: #718096;">支持:</span>
                        <span style="background: rgba(0, 114, 206, 0.2); padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">订单查询</span>
                        <span style="background: rgba(0, 179, 136, 0.2); padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">状态检查</span>
                        <span style="background: rgba(123, 97, 255, 0.2); padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">数据分析</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 💡 查询示例")
        
        examples = [
            "订单 4200000001 的当前状态",
            "查询所有待处理的订单",
            "订单号 4200000002 的发货信息",
            "昨天创建的订单有哪些"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                st.session_state.query_input = example
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📊 快速统计")
        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("今日", "24")
        with col6:
            st.metric("本周", "156")
        with col7:
            st.metric("成功率", "99.99%")
        
        st.markdown('</div>', unsafe_allow_html=True)

def handle_query(query_text):
    """处理查询请求"""
    if not query_text.strip():
        st.warning("请输入查询内容")
        return
    
    with st.spinner("正在分析您的查询..."):
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
                    display_results(result, query_text)
                else:
                    st.error(f"查询失败: {result.get('message', '未知错误')}")
            else:
                st.error(f"服务器错误: {response.status_code}")
                
        except Exception as e:
            st.error(f"查询异常: {str(e)}")

def display_results(result, original_query):
    """显示查询结果"""
    st.markdown("### 📋 查询结果")
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
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
                <div class="metric-value">{result.get('log_id', '-')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        status = result.get('sap_status', '').lower()
        if '完成' in status:
            color = "#00B388"
            icon = "✅"
        elif '处理' in status:
            color = "#0072CE"
            icon = "🔄"
        else:
            color = "#FF6B6B"
            icon = "⚠️"
        
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">状态</div>
                <div style="font-size: 1.8rem; color: {color}; margin: 0.5rem 0;">{icon}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # AI回复
    st.markdown("### 🤖 AI助手 分析报告")
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
        "response": result.get('final_response', '-')
    }
    st.session_state.query_history.insert(0, history_item)

def render_history_page():
    """渲染历史记录页面"""
    render_header()
    
    st.markdown(
        """
        <h2 style="margin-bottom: 0.5rem;">📜 查询历史</h2>
        <p style="color: #A0AEC0; margin-bottom: 2rem;">查看您的查询记录</p>
        """,
        unsafe_allow_html=True
    )
    
    if st.session_state.query_history:
        for idx, item in enumerate(st.session_state.query_history[:20]):
            with st.container():
                st.markdown(
                    f"""
                    <div class="history-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span class="history-time">{item['timestamp']}</span>
                                <span style="margin-left: 1rem; background: rgba(0, 114, 206, 0.2); padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">
                                    订单 {item['order_id']}
                                </span>
                            </div>
                            <span style="font-size: 0.8rem; color: {'#00B388' if '完成' in item['status'] else '#FF6B6B'}">
                                {item['status']}
                            </span>
                        </div>
                        <div class="history-query">{item['query']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                with st.expander("查看详情", key=f"expander_{idx}"):
                    st.markdown(f"**AI回复:** {item['response']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 复制结果", key=f"copy_{idx}"):
                            st.success("已复制到剪贴板")
                    with col2:
                        if st.button("🔁 重新查询", key=f"re_query_{idx}"):
                            handle_query(item['query'])
    else:
        st.info("暂无查询历史记录")

# ==================== 主程序 ====================

def main():
    """主程序入口"""
    
    if st.session_state.user_id is None:
        render_login_page()
    else:
        # 渲染侧边栏
        render_sidebar()
        
        # 根据选择渲染页面
        if st.session_state.current_tab == "查询":
            render_query_page()
        elif st.session_state.current_tab == "历史":
            render_history_page()
        elif st.session_state.current_tab == "仪表板":
            st.markdown("## 📊 数据仪表板")
            st.info("仪表板功能开发中...")
        else:  # 设置
            st.markdown("## ⚙️ 系统设置")
            st.info("设置功能开发中...")

if __name__ == "__main__":
    main()
