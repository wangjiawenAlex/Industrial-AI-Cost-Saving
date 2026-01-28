import streamlit as st
import requests
import json
from datetime import datetime
import logging
import os
import time
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

st.set_page_config(
    page_title="施耐德万高 — 订单查询系统",
    page_icon="sw.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logger.error(f"图片加载失败: {e}")
        return None

PRIMARY_GREEN = "#3DCD58"
GRAY = "#626469"
YELLOW = "#FFD100"
ORANGE = "#E47F00"
RED = "#B10043"
BLUE = "#42B4E6"
WHITE = "#FFFFFF"
BLACK = "#000000"

LEFT_PANEL_HTML = """
<div class="login-left-panel">
    <div style="z-index: 10; position: relative;">
        <div style="margin-bottom: 60px;">
            <div class="logo-text">Schneider Electric</div>
            <div class="logo-subtext">订单查询系统</div>
        </div>
        <div style="animation: fadeInUp 1s ease-out 0.2s both;">
            <div class="welcome-title">欢迎使用<br>施耐德订单查询系统!</div>
            <div class="welcome-desc">
                一键登录,畅享便捷。在这里,您可随时查询订单状态,获取专属业务支持与服务。专属订单管家,为您提供一站式智慧服务!
            </div>
        </div>
        <div style="display: flex; gap: 12px; margin-top: 50px; animation: fadeInUp 1s ease-out 0.4s both;">
            <div style="width: 30px; height: 10px; background: white; border-radius: 5px;"></div>
            <div style="width: 10px; height: 10px; background: rgba(255,255,255,0.4); border-radius: 50%;"></div>
            <div style="width: 10px; height: 10px; background: rgba(255,255,255,0.4); border-radius: 50%;"></div>
        </div>
    </div>
</div>
"""

CSS_LOGIN = """
<style>
    .login-left-panel {
        position: fixed; left: 0; top: 0; width: 50%; height: 100vh;
        background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
        z-index: 0; padding: 80px 60px;
        display: flex; flex-direction: column; justify-content: center; overflow: hidden;
    }
    @media (max-width: 900px) { .login-left-panel { display: none; } }

    .logo-text { font-family: sans-serif; font-size: 28px; font-weight: 700; color: white; margin-bottom: 5px; }
    .logo-subtext { font-family: sans-serif; font-size: 14px; color: rgba(255, 255, 255, 0.9); margin-bottom: 60px; }
    .welcome-title { font-family: sans-serif; font-size: 42px; font-weight: 700; color: white; line-height: 1.3; margin-bottom: 30px; }
    .welcome-desc { font-family: sans-serif; font-size: 18px; color: rgba(255, 255, 255, 0.95); line-height: 1.8; max-width: 520px; }

    div[data-baseweb="input"] {
        border-radius: 12px !important; border: 2px solid #E5E5E5 !important; padding: 8px !important; background: white !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #3DCD58 !important; box-shadow: 0 0 0 4px rgba(61, 205, 88, 0.1) !important;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(30px, -30px) rotate(120deg); }
        66% { transform: translate(-20px, 20px) rotate(240deg); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .login-left-panel::before {
        content: ''; position: absolute; top: -50%; right: -20%; width: 600px; height: 600px;
        background: rgba(255, 255, 255, 0.05); border-radius: 50%; animation: float 20s ease-in-out infinite;
    }
    .login-left-panel::after {
        content: ''; position: absolute; bottom: -30%; left: -15%; width: 500px; height: 500px;
        background: rgba(255, 255, 255, 0.03); border-radius: 50%; animation: float 15s ease-in-out infinite reverse;
    }
</style>
"""

CSS_QUERY_PAGE = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* 全局字体和基础设置 */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    overflow-x: hidden;
}}

* {{
    box-sizing: border-box;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

/* 容器最大宽度限制 */
.main .block-container {{
    max-width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

.schneider-header {{
    background: linear-gradient(135deg, {PRIMARY_GREEN} 0%, #2BA845 100%);
    padding: 1.5rem 2rem;
    border-radius: 0;
    box-shadow: 0 4px 12px rgba(61, 205, 88, 0.2);
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 1.5rem -1rem;
    width: calc(100% + 2rem);
    overflow: hidden;
}}

.schneider-logo {{
    display: flex;
    align-items: center;
    gap: 15px;
    min-width: 0;
    flex: 1;
}}

.logo-icon {{
    width: 50px;
    height: 50px;
    min-width: 50px;
    background: {WHITE};
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 24px;
    color: {PRIMARY_GREEN};
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    flex-shrink: 0;
}}

.header-title {{
    color: {WHITE};
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.header-subtitle {{
    color: rgba(255,255,255,0.9);
    font-size: 0.95rem;
    margin: 0;
    font-weight: 400;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.user-info {{
    color: {WHITE};
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
    flex-shrink: 0;
    padding-right: 1rem;
}}

.query-card {{
    background: {WHITE};
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.06);
    overflow: hidden;
    width: 100%;
}}

.query-title {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {GRAY};
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}}

.query-icon {{
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, {PRIMARY_GREEN}, #2BA845);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
}}

.stButton > button {{
    background: linear-gradient(135deg, {PRIMARY_GREEN} 0%, #2BA845 100%);
    color: {WHITE};
    border: none;
    border-radius: 10px;
    padding: 0.75rem 2rem;
    font-size: 1.05rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(61, 205, 88, 0.3);
    width: 100%;
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(61, 205, 88, 0.4);
}}

.stButton > button:active {{
    transform: translateY(0);
}}

.stTextArea textarea {{
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    padding: 1rem;
    font-size: 1rem;
    transition: all 0.3s ease;
}}

.stTextArea textarea:focus {{
    border-color: {PRIMARY_GREEN};
    box-shadow: 0 0 0 3px rgba(61, 205, 88, 0.1);
}}

.metric-card {{
    background: linear-gradient(135deg, {WHITE} 0%, #F9FAFB 100%);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
    transition: all 0.3s ease;
    overflow: hidden;
    width: 100%;
}}

.metric-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}}

.metric-label {{
    font-size: 0.85rem;
    color: {GRAY};
    font-weight: 500;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.metric-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {PRIMARY_GREEN};
    margin: 0;
    word-break: break-all;
}}

.ai-response {{
    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
    border-left: 4px solid {PRIMARY_GREEN};
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    box-shadow: 0 2px 8px rgba(61, 205, 88, 0.1);
    overflow: hidden;
    width: 100%;
}}

.ai-response-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: {PRIMARY_GREEN};
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}}

.ai-response-content {{
    font-size: 1rem;
    color: {GRAY};
    line-height: 1.6;
    word-break: break-word;
}}

.css-1d391kg {{
    background: #F9FAFB;
}}

.sidebar-title {{
    font-size: 1.2rem;
    font-weight: 700;
    color: {GRAY};
    margin-bottom: 1rem;
    padding: 0 1rem;
}}

.history-card {{
    background: {WHITE};
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    border-left: 3px solid {PRIMARY_GREEN};
    transition: all 0.3s ease;
    cursor: pointer;
}}

.history-card:hover {{
    transform: translateX(5px);
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}}

.example-box {{
    background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
    border-radius: 12px;
    padding: 1.2rem;
    border-left: 4px solid {YELLOW};
    margin-bottom: 1.5rem;
    overflow: hidden;
    width: 100%;
}}

.example-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {ORANGE};
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}}

.example-item {{
    font-size: 0.9rem;
    color: {GRAY};
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    word-break: break-word;
}}

.example-item:last-child {{
    border-bottom: none;
}}

/* 施耐德品牌标识样式 - 移除背景 */
.schneider-brand {{
    text-align: center;
    margin-top: 1.5rem;
}}

.schneider-logo-img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}}

/* 响应式设计 */
@media (max-width: 1200px) {{
    .schneider-header {{
        padding: 1.2rem 1.5rem;
    }}
    
    .header-title {{
        font-size: 1.5rem;
    }}
    
    .header-subtitle {{
        font-size: 0.85rem;
    }}
    
    .query-card {{
        padding: 1.5rem;
    }}
    
    .stButton > button {{
        padding: 0.7rem 1.8rem;
        font-size: 1rem;
        min-height: 46px;
    }}
}}

@media (max-width: 768px) {{
    .schneider-header {{
        flex-direction: column;
        align-items: flex-start;
        padding: 1rem;
        gap: 1rem;
    }}
    
    .schneider-logo {{
        width: 100%;
    }}
    
    .header-title {{
        font-size: 1.3rem;
    }}
    
    .header-subtitle {{
        font-size: 0.8rem;
    }}
    
    .user-info {{
        width: 100%;
        justify-content: flex-start;
    }}
    
    .query-card {{
        padding: 1rem;
    }}
    
    .query-title {{
        font-size: 1.2rem;
    }}
    
    .metric-card {{
        padding: 0.8rem;
    }}
    
    .metric-label {{
        font-size: 0.75rem;
    }}
    
    .metric-value {{
        font-size: 1.2rem;
    }}
    
    .example-box {{
        padding: 1rem;
    }}
    
    .example-item {{
        font-size: 0.85rem;
    }}
    
    .ai-response {{
        padding: 1rem;
    }}
    
    .ai-response-title {{
        font-size: 1rem;
    }}
    
    .ai-response-content {{
        font-size: 0.95rem;
    }}
    
    .stButton > button {{
        padding: 0.65rem 1.5rem;
        font-size: 0.95rem;
        border-radius: 8px;
        min-height: 44px;
    }}
    
    .stTextArea textarea {{
        font-size: 0.95rem;
        padding: 0.8rem;
    }}
}}

@media (max-width: 480px) {{
    .schneider-header {{
        padding: 0.8rem;
    }}
    
    .header-title {{
        font-size: 1.1rem;
    }}
    
    .header-subtitle {{
        font-size: 0.75rem;
    }}
    
    .logo-icon {{
        width: 40px;
        height: 40px;
        min-width: 40px;
        font-size: 20px;
    }}
    
    .query-title {{
        font-size: 1rem;
    }}
    
    .query-card {{
        padding: 0.8rem;
    }}
    
    .metric-card {{
        padding: 0.6rem;
    }}
    
    .metric-label {{
        font-size: 0.7rem;
    }}
    
    .metric-value {{
        font-size: 1rem;
    }}
    
    .example-box {{
        padding: 0.8rem;
    }}
    
    .example-title {{
        font-size: 0.9rem;
    }}
    
    .example-item {{
        font-size: 0.8rem;
    }}
    
    .ai-response {{
        padding: 0.8rem;
    }}
    
    .ai-response-title {{
        font-size: 0.95rem;
    }}
    
    .ai-response-content {{
        font-size: 0.9rem;
    }}
    
    .stButton > button {{
        padding: 0.55rem 1.2rem;
        font-size: 0.9rem;
        border-radius: 8px;
    }}
    
    .stTextArea textarea {{
        font-size: 0.9rem;
        padding: 0.7rem;
    }}
    
    .user-info {{
        font-size: 0.85rem;
    }}
}}
</style>
"""

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "current_response" not in st.session_state:
    st.session_state.current_response = None

def login_page():
    st.markdown(CSS_LOGIN, unsafe_allow_html=True)
    st.markdown(LEFT_PANEL_HTML, unsafe_allow_html=True)

    col_bg, col_form = st.columns([1, 1])

    with col_bg:
        st.empty()

    with col_form:
        st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
        _, form_container, _ = st.columns([1, 8, 1])
        
        with form_container:
            st.markdown("## 登录账户")
            st.markdown("<p style='color: #666; margin-bottom: 30px;'>输入您的凭据以访问系统</p>", unsafe_allow_html=True)

            username = st.text_input("用户名", placeholder="请输入用户名", label_visibility="collapsed")
            st.markdown('<div style="height: 15px"></div>', unsafe_allow_html=True)
            password = st.text_input("密码", type="password", placeholder="请输入密码", label_visibility="collapsed")

            st.markdown("""
            <div style="display: flex; justify-content: space-between; margin: 15px 0 0 0; font-size: 14px; color: #666;">
                <label style="display: flex; align-items: center; cursor: pointer;">
                    <input type="checkbox" style="margin-right: 5px; accent-color: #3DCD58;"> 记住我
                </label>
                <a href="#" style="color: #3DCD58; text-decoration: none;">忘记密码?</a>
            </div>
            """, unsafe_allow_html=True)

            if st.button("登录", use_container_width=True):
                if not username or not password:
                    st.error("⚠️ 用户名和密码不能为空")
                else:
                    st.info(f"📝 正在验证...")
                    logger.info(f"🔐 用户尝试登录: {username}")

                    try:
                        login_url = f"{BACKEND_BASE_URL}/api/login"
                        response = requests.post(
                            login_url,
                            json={"username": username, "password": password},
                            timeout=10,
                            proxies={"http": None, "https": None}
                        )

                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success"):
                                st.session_state.user_id = result.get("user_id")
                                st.session_state.username = username
                                st.success(result.get("message", "登录成功"))
                                time.sleep(0.5)
                                st.experimental_rerun()
                            else:
                                st.error(result.get("message", "登录失败"))
                        else:
                            st.error(f"服务器响应错误: {response.status_code}")

                    except requests.exceptions.ConnectionError:
                        st.error("❌ 无法连接到后端服务,请确保 FastAPI 服务已启动")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ 请求超时,请稍后重试")
                    except Exception as e:
                        st.error(f"登录异常: {str(e)}")

            st.markdown("""
                <div style="text-align: center; margin-top: 30px; font-size: 13px; color: #999;">
                    还没有账户?<a href="#" style="color: #3DCD58; text-decoration: none;">立即注册</a>
                </div>
            """, unsafe_allow_html=True)

def query_page():
    st.markdown(CSS_QUERY_PAGE, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="schneider-header">
        <div class="schneider-logo">
            <div class="logo-icon">SE</div>
            <div>
                <div class="header-title">Schneider Electric</div>
                <div class="header-subtitle">万高数据订单查询系统</div>
            </div>
        </div>
        <div class="user-info">
            <span>👋 欢迎, {st.session_state.username}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, {PRIMARY_GREEN}, #2BA845); border-radius: 10px; margin-bottom: 1.5rem;">
            <div style="color: white; font-size: 1.3rem; font-weight: 700;">📋 查询历史</div>
            <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; margin-top: 0.3rem;">History Records</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.query_history = []
            st.session_state.current_response = None
            st.experimental_rerun()

        st.markdown("---")

        if st.session_state.query_history:
            for idx, item in enumerate(st.session_state.query_history[:15]):
                with st.expander(f"📝 订单 {item['order_id']}", expanded=False):
                    st.markdown(f"**🕒 时间:** {item['timestamp']}")
                    st.markdown(f"**📦 订单号:** `{item['order_id']}`")
                    st.markdown(f"**📊 状态:** `{item['status']}`")
                    st.markdown(f"**❓ 查询:** {item['query'][:50]}...")
                    if st.button("🔍 查看详情", key=f"view_{idx}"):
                        st.session_state.current_response = item
        else:
            st.info("暂无查询历史")

    col_main, col_side = st.columns([7, 3])

    with col_main:
        st.markdown("""
        <div class="query-card">
            <div class="query-title">
                <div class="query-icon">🔍</div>
                订单查询
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        query_text = st.text_area(
            "请输入查询内容",
            placeholder="例如:查询订单 4200000001 的状态\n或者:我想知道订单号 4200000002 现在怎么样了\n支持自然语言输入...",
            height=120,
            label_visibility="collapsed"
        )

        if st.button(" 开始查询", use_container_width=True, key="main_query_btn"):
            if not query_text.strip():
                st.error("❌ 请输入查询内容")
            else:
                with st.spinner("🔄 正在处理您的查询..."):
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
                                st.session_state.current_response = {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "query": query_text,
                                    "order_id": result.get('order_id', '-'),
                                    "status": result.get('sap_status', '-'),
                                    "response": result.get('final_response', '-'),
                                    "log_id": result.get('log_id', '-')
                                }
                                
                                st.session_state.query_history.insert(0, st.session_state.current_response)
                                
                                st.success("✅ 查询成功!")
                                st.experimental_rerun()
                            else:
                                st.error(f"❌ 查询失败: {result.get('message', '未知错误')}")
                        else:
                            st.error(f"❌ 后端错误: {response.status_code}")

                    except requests.exceptions.ConnectionError:
                        st.error("❌ 无法连接到后端服务,请确保 FastAPI 服务已启动")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ 请求超时,请稍后重试")
                    except Exception as e:
                        st.error(f"❌ 异常: {str(e)}")

        if st.session_state.current_response:
            st.markdown("---")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📦 订单号</div>
                    <div class="metric-value">{st.session_state.current_response['order_id']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📊 订单状态</div>
                    <div class="metric-value">{st.session_state.current_response['status']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🆔 查询 ID</div>
                    <div class="metric-value">{st.session_state.current_response['log_id']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="ai-response">
                <div class="ai-response-title">🤖 AI 助手回复</div>
                <div class="ai-response-content">{st.session_state.current_response['response']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        st.markdown(f"""
        <div class="example-box">
            <div class="example-title">💡 查询示例</div>
            <div class="example-item">• 查询订单 4200000001 的状态</div>
            <div class="example-item">• 我的订单 4200000002 怎么样了</div>
            <div class="example-item">• 订单号 4200000003 完成了吗</div>
            <div class="example-item">• 帮我查一下订单 4200000004</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-size: 1rem; font-weight: 600; color: {GRAY}; margin-bottom: 0.8rem;">ℹ️ 系统信息</div>
            <div style="font-size: 0.85rem; color: {GRAY}; line-height: 1.6;">
                <div style="margin-bottom: 0.5rem;">✅ 实时查询 SAP 系统</div>
                <div style="margin-bottom: 0.5rem;">✅ 自然语言理解</div>
                <div style="margin-bottom: 0.5rem;">✅ 智能订单匹配</div>
                <div>✅ 历史记录保存</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
        try:
            st.image("sw.png", use_column_width=True)
        except:
            img_base64 = get_image_base64("sw.png")
            if img_base64:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 1.5rem;">
                    <img src="data:image/png;base64,{img_base64}"
                         style="max-width: 100%; height: auto;"
                         alt="Schneider Electric Logo">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {PRIMARY_GREEN} 0%, #2BA845 100%);
                            border-radius: 12px; padding: 1.5rem; text-align: center; margin-top: 1.5rem;">
                    <div style="color: white; font-size: 1.8rem; font-weight: 800;">SE</div>
                    <div style="color: white; font-size: 0.9rem; font-weight: 600;">Schneider Electric</div>
                </div>
                """, unsafe_allow_html=True)

def main():
    if st.session_state.user_id is None:
        login_page()
    else:
        query_page()

if __name__ == "__main__":
    main()