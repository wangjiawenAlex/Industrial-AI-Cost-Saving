"""
Streamlit 前端应用（美化版）
公司名：施耐德万高
颜色：高科技蓝色（#0072CE）与绿色（#00B388）
标语：万高数据，一问直答

说明：原始 frontend.py 的美化版本，保留现有功能与 API 调用逻辑，仅对 UI/样式、布局与体验进行了增强
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

# 禁用HTTP代理 - 解决502问题
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="施耐德万高 — 万高数据，一问直答",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 主题色（方便全局替换）
PRIMARY_BLUE = "#0072CE"
PRIMARY_GREEN = "#00B388"

# ==================== 安全版 CSS（不含任何 Python 变量） ====================
css_safe = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

/* 全局按钮样式 */
.stButton>button{
  width: 100%;
  height: 2.6rem;
  font-size: 1rem;
  font-weight: 700;
  border-radius: 8px;
  border: none;
  box-shadow: none;
}

/* 卡片样式 */
.card{
  padding: 0.9rem;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  border: 1px solid rgba(0,0,0,0.04);
}

.metric-custom{
  background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
  padding: 0.6rem;
  border-radius: 8px;
}

.info-box { padding: 0.9rem; border-radius: 8px; background-color: #eef8fb; border: 1px solid rgba(0,114,206,0.08); }

.small-muted { color: #6b7280; font-size: 0.9rem; }

</style>
"""

# ==================== 可变量版 CSS（只有需要替换的颜色/渐变，安全地通过字符串拼接构建）
css_vars = (
    "<style>"
    " .header-banner{ background: linear-gradient(90deg, " + PRIMARY_BLUE + " 0%, " + PRIMARY_GREEN + " 100%); color: white; padding: 1.1rem 1.4rem; border-radius: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.12); margin-bottom: 1rem; }"
    " .brand-title{ font-size: 1.6rem; font-weight: 700; letter-spacing: 0.2px; }"
    " .tagline{ opacity: 0.92; font-size: 0.95rem; margin-top: 0.1rem; }"
    " .btn-primary>button{ background: linear-gradient(90deg, " + PRIMARY_BLUE + ", " + PRIMARY_GREEN + "); color: white; }"
    "</style>"
)

# 注入 CSS（先安全版，再变量版）
st.markdown(css_safe + css_vars, unsafe_allow_html=True)

# ==================== 后端配置 ====================
BACKEND_BASE_URL = os.getenv(
    "BACKEND_BASE_URL",
    "http://127.0.0.1:8000"  # 本地兜底
)

# ==================== Session State 管理 ====================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# ==================== 公共组件 / helper ====================

def render_header():
    """渲染顶部品牌 banner"""
    left, mid, right = st.columns([3, 6, 1])
    with mid:
        st.markdown(
            """
            <div class="header-banner">
                <div class="brand-title">施耐德万高</div>
                <div class="tagline">万高数据，一问直答</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==================== 页面函数 ====================

def login_page():
    """登录页面"""
    render_header()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 系统登录")
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
                login_url = f"{BACKEND_BASE_URL}/api/login"
                logger.info(f"发送请求到: {login_url}")

                response = requests.post(
                    login_url,
                    json={"username": username, "password": password},
                    timeout=10,
                    proxies={"http": None, "https": None}
                )

                logger.info(f"收到响应: 状态码={response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        st.session_state.user_id = result.get("user_id")
                        st.session_state.username = username
                        st.success(result.get("message", "登录成功"))
                        st.rerun()
                    else:
                        st.error(result.get("message", "登录失败"))
                else:
                    st.error(f"登录失败: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务，请确保 FastAPI 服务已启动")
            except requests.exceptions.Timeout:
                st.error("请求超时，请稍后重试")
            except Exception as e:
                st.error(f"登录异常: {str(e)}")

        st.markdown("---")
        st.markdown("""
        <div class="small-muted">**Demo 账户说明：**<br>
        - 首次登录时，系统会自动创建新用户<br>
        - 您可以使用任意用户名和密码进行登录<br>
        - 所有查询都会被记录在日志中用于运维审计
        </div>
        """, unsafe_allow_html=True)


def query_page():
    """查询页面"""
    render_header()

    # 顶部导航栏
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"### 👋 欢迎，{st.session_state.username}！")
        st.markdown("<div class='small-muted'>在这里输入自然语言查询，系统会返回 SAP 订单信息并由 AI 美化回答。</div>", unsafe_allow_html=True)
    with col3:
        if st.button("退出登录"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.query_history = []
            st.rerun()

    st.markdown("---")

    # 主查询区域
    outer_col1, outer_col2 = st.columns([3, 1])
    with outer_col1:
        st.markdown("## 📋 订单查询")
        query_text = st.text_area(
            "请输入您的查询（支持自然语言）",
            placeholder="例如：查询订单 4200000001 的状态
或者：我想知道订单号 4200000002 现在怎么样了",
            height=120
        )

        if st.button("🔍 查询", use_container_width=True, key="query_btn"):
            if not query_text.strip():
                st.error("请输入查询内容")
            else:
                with st.spinner("正在处理您的查询..."):
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
                                st.markdown("### ✅ 查询结果")

                                # 指标卡
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.markdown(f"<div class='card metric-custom'><strong>订单号</strong><div style='font-size:18px;margin-top:6px'>{result.get('order_id','-')}</div></div>", unsafe_allow_html=True)
                                with c2:
                                    st.markdown(f"<div class='card metric-custom'><strong>订单状态</strong><div style='font-size:18px;margin-top:6px'>{result.get('sap_status','-')}</div></div>", unsafe_allow_html=True)
                                with c3:
                                    st.markdown(f"<div class='card metric-custom'><strong>查询 ID</strong><div style='font-size:18px;margin-top:6px'>{result.get('log_id','-')}</div></div>", unsafe_allow_html=True)

                                st.markdown("---")
                                st.markdown("### 🤖 AI 回复")
                                st.markdown(f"<div class='info-box'>{result.get('final_response','-')}</div>", unsafe_allow_html=True)

                                # 添加到历史记录
                                st.session_state.query_history.insert(0, {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "query": query_text,
                                    "order_id": result.get('order_id','-'),
                                    "status": result.get('sap_status','-'),
                                    "response": result.get('final_response','-')
                                })
                            else:
                                st.error(f"❌ 查询失败: {result.get('message','未知错误')}")
                        else:
                            st.error(f"后端错误: {response.status_code}")

                    except requests.exceptions.ConnectionError:
                        st.error("❌ 无法连接到后端服务，请确保 FastAPI 服务已启动")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ 请求超时，请稍后重试")
                    except Exception as e:
                        st.error(f"异常: {str(e)}")

    with outer_col2:
        st.markdown("**查询示例：**")
        st.markdown("- 订单 4200000001 的状态
- 查询订单 4200000002
- 订单号 4200000003 现在怎么样
- 我的订单 4200000004 完成了吗")
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
