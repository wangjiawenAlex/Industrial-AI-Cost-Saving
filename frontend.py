"""
Streamlit 前端应用
提供用户界面用于登录和查询
"""

import streamlit as st
import requests
import json
from datetime import datetime
import logging
import os

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 禁用HTTP代理 - 解决502问题
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="SAP 订单查询系统",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 2.5rem;
        font-size: 1rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 后端配置 ====================

# BACKEND_URL = "http://127.0.0.1:8000" 本地调试使用，提供参考

BACKEND_URL = os.getenv(
    "BACKEND_API_URL",
    "http://127.0.0.1:8000"  # 本地开发兜底
)


# ==================== Session State 管理 ====================

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []


# ==================== 页面函数 ====================

def login_page():
    """登录页面"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 SAP 订单查询系统")
        st.markdown("---")
        
        username = st.text_input("用户名", placeholder="输入用户名")
        password = st.text_input("密码", type="password", placeholder="输入密码")
        
        if st.button("登录", use_container_width=True):
            if not username or not password:
                st.error("用户名和密码不能为空")
                return
            
            st.info(f"📝 正在登录，用户: {username}")
            logger.info(f"🔐 用户点击登陆: {username}")
            
            try:
                login_url = f"{BACKEND_URL}/api/login"
                st.write(f"调试: 请求URL = {login_url}")
                logger.info(f"发送请求到: {login_url}")
                
                response = requests.post(
                    login_url,
                    json={"username": username, "password": password},
                    timeout=10,
                    proxies={"http": None, "https": None}  # 禁用代理
                )
                
                logger.info(f"收到响应: 状态码={response.status_code}")
                st.write(f"调试: 响应状态码 = {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result["success"]:
                        st.session_state.user_id = result["user_id"]
                        st.session_state.username = username
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.error(f"登录失败: {response.status_code}")
                    st.write(f"调试: 响应内容 = {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务，请确保 FastAPI 服务已启动（端口 8000）")
            except requests.exceptions.Timeout:
                st.error("请求超时，请稍后重试")
            except Exception as e:
                st.error(f"登录异常: {str(e)}")
        
        st.markdown("---")
        st.markdown("""
        **Demo 账户说明：**
        - 首次登录时，系统会自动创建新用户
        - 您可以使用任意用户名和密码进行登录
        - 所有查询都会被记录在日志中用于运维审计
        """)


def query_page():
    """查询页面"""
    
    # 顶部导航栏
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"### 👋 欢迎，{st.session_state.username}！")
    with col3:
        if st.button("退出登录"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.query_history = []
            st.rerun()
    
    st.markdown("---")
    
    # 主查询区域
    st.markdown("## 📋 订单查询")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query_text = st.text_area(
            "请输入您的查询（支持自然语言）",
            placeholder="例如：查询订单 4200000001 的状态\n或者：我想知道订单号 4200000002 现在怎么样了",
            height=100
        )
    
    with col2:
        st.markdown("**查询示例：**")
        st.markdown("""
        - 订单 4200000001 的状态
        - 查询订单 4200000002
        - 订单号 4200000003 现在怎么样
        - 我的订单 4200000004 完成了吗
        """)
    
    if st.button("🔍 查询", use_container_width=True, type="primary"):
        if not query_text.strip():
            st.error("请输入查询内容")
        else:
            with st.spinner("正在处理您的查询..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/query",
                        json={
                            "user_id": st.session_state.user_id,
                            "query_text": query_text
                        },
                        timeout=30,
                        proxies={"http": None, "https": None}  # 禁用代理
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["success"]:
                            st.markdown("### ✅ 查询结果")
                            
                            # 显示订单信息
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("订单号", result["order_id"])
                            with col2:
                                st.metric("订单状态", result["sap_status"])
                            with col3:
                                st.metric("查询 ID", result["log_id"])
                            
                            st.markdown("---")
                            
                            # 显示 AI 美化后的回复
                            st.markdown("### 🤖 AI 回复")
                            st.info(result["final_response"])
                            
                            # 添加到历史记录
                            st.session_state.query_history.insert(0, {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "query": query_text,
                                "order_id": result["order_id"],
                                "status": result["sap_status"],
                                "response": result["final_response"]
                            })
                        else:
                            st.error(f"❌ 查询失败: {result['message']}")
                    else:
                        st.error(f"后端错误: {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务，请确保 FastAPI 服务已启动")
                except requests.exceptions.Timeout:
                    st.error("⏱️ 请求超时，请稍后重试")
                except Exception as e:
                    st.error(f"异常: {str(e)}")
    
    # 查询历史
    st.markdown("---")
    st.markdown("## 📜 查询历史")
    
    if st.session_state.query_history:
        for idx, item in enumerate(st.session_state.query_history[:10]):
            with st.expander(f"查询 #{idx+1} - {item['timestamp']} - 订单 {item['order_id']}"):
                st.markdown(f"**用户查询：** {item['query']}")
                st.markdown(f"**订单状态：** {item['status']}")
                st.markdown(f"**AI 回复：** {item['response']}")
    else:
        st.info("暂无查询历史")


# ==================== 主程序 ====================

def main():
    """主程序入口"""
    
    if st.session_state.user_id is None:
        login_page()
    else:
        query_page()


if __name__ == "__main__":
    main()
