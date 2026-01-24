"""
FastAPI 后端应用
处理用户认证、查询、日志记录等核心业务逻辑
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import json

from models import User, QueryLog, get_db, engine, Base
from sap_mock import query_sap_order_status, validate_order_id
from llm_handler import LLMHandler
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title="SAP Query API", version="1.0.0")

# 请求日志中间件 - 记录所有请求
@app.middleware("http")
async def log_requests(request, call_next):
    """记录所有HTTP请求"""
    logger.info(f"📨 收到请求: {request.method} {request.url.path}")
    logger.debug(f"   Headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        logger.info(f"📤 返回响应: {request.method} {request.url.path} -> {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ 请求处理异常: {str(e)}", exc_info=True)
        raise

# 配置 CORS，允许 Streamlit 前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 LLM 处理器
try:
    llm_handler = LLMHandler()
except ValueError as e:
    print(f"⚠️  警告: {e}")
    print("💡 解决方案: 设置环境变量 DEEPSEEK_API_KEY")
    print("   Windows: set DEEPSEEK_API_KEY=your_api_key")
    print("   PowerShell: $env:DEEPSEEK_API_KEY='your_api_key'")
    llm_handler = None


# 启动事件 - 应用启动时的诊断
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化和诊断"""
    print("\n" + "="*60)
    print("🚀 SAP Query API 启动中...")
    print("="*60)
    
    # 检查数据库
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if tables:
            print(f"✅ 数据库已初始化 - 表: {', '.join(tables)}")
        else:
            print("⚠️  数据库表未初始化")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
    
    # 检查 LLM
    if llm_handler:
        print("✅ LLM 处理器初始化成功")
    else:
        print("⚠️  LLM 处理器未初始化 (DEEPSEEK_API_KEY 未设置)")
    
    # 检查 SAP Mock
    print("✅ SAP Mock 服务已加载")
    
    print("="*60)
    print("✅ 应用启动完成!")
    print("📍 API 地址: http://127.0.0.1:8000")
    print("📍 API 文档: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")


# ==================== 数据模型 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    message: str
    user_id: int = None


class QueryRequest(BaseModel):
    """查询请求"""
    user_id: int
    query_text: str


class QueryResponse(BaseModel):
    """查询响应"""
    success: bool
    message: str
    order_id: str = None
    sap_status: str = None
    final_response: str = None
    log_id: int = None


# ==================== 用户认证 ====================

@app.post("/api/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    Args:
        request: 包含用户名和密码
        db: 数据库会话
        
    Returns:
        登录结果
    """
    
    logger.debug(f"📝 收到登录请求: username={request.username}")
    
    try:
        # 从数据库查询用户
        user = db.query(User).filter(User.username == request.username).first()
        
        if not user:
            # 如果用户不存在，创建新用户（Demo 模式）
            logger.info(f"👤 创建新用户: {request.username}")
            try:
                new_user = User(username=request.username, password=request.password)
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                logger.info(f"✅ 新用户创建成功: ID={new_user.id}")
                return LoginResponse(
                    success=True,
                    message=f"欢迎 {request.username}！新用户已创建",
                    user_id=new_user.id
                )
            except Exception as e:
                db.rollback()
                logger.error(f"❌ 创建用户失败: {str(e)}", exc_info=True)
                return LoginResponse(
                    success=False,
                    message=f"创建用户失败: {str(e)}"
                )
        
        # 验证密码（Demo 模式下不做加密验证）
        if user.password != request.password:
            logger.warning(f"❌ 密码错误: {request.username}")
            return LoginResponse(
                success=False,
                message="密码错误"
            )
        
        logger.info(f"✅ 登录成功: {user.username} (ID={user.id})")
        return LoginResponse(
            success=True,
            message=f"登录成功，欢迎 {user.username}！",
            user_id=user.id
        )
    
    except Exception as e:
        logger.error(f"❌ 登录接口异常: {str(e)}", exc_info=True)
        return LoginResponse(
            success=False,
            message=f"登录异常: {str(e)}")
        
    return LoginResponse(
        success=True,
        message=f"登录成功，欢迎 {user.username}！",
        user_id=user.id
    )


# ==================== 查询处理 ====================

@app.post("/api/query", response_model=QueryResponse)
def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    处理用户查询
    流程：意图识别 -> SAP 查询 -> 结果美化 -> 日志记录
    
    Args:
        request: 包含 user_id 和 query_text
        db: 数据库会话
        
    Returns:
        查询结果
    """
    
    # 验证用户
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    # 初始化日志记录
    log_entry = QueryLog(
        user_id=request.user_id,
        raw_query=request.query_text
    )
    
    try:
        # 第一步：LLM 意图识别
        if not llm_handler:
            return QueryResponse(
                success=False,
                message="LLM 服务未初始化，请检查 DEEPSEEK_API_KEY 环境变量"
            )
        
        success, intent_result = llm_handler.extract_intent(request.query_text)
        
        if not success:
            log_entry.status = "error"
            log_entry.llm_extracted_intent = json.dumps(intent_result, ensure_ascii=False)
            db.add(log_entry)
            db.commit()
            
            return QueryResponse(
                success=False,
                message=f"意图识别失败: {intent_result.get('error', '未知错误')}"
            )
        
        order_id = intent_result.get("order_id", "").strip()
        log_entry.llm_extracted_intent = json.dumps(intent_result, ensure_ascii=False)
        
        # 验证订单号
        if not order_id or not validate_order_id(order_id):
            log_entry.status = "error"
            db.add(log_entry)
            db.commit()
            
            return QueryResponse(
                success=False,
                message=f"无法识别有效的订单号。您的查询: {request.query_text}"
            )
        
        # 第二步：SAP 查询（目前硬编码返回"制作中"）
        sap_response = query_sap_order_status(order_id)
        log_entry.sap_raw_response = json.dumps(sap_response, ensure_ascii=False)
        
        # 第三步：LLM 结果美化
        success, beautified_response = llm_handler.beautify_response(
            request.query_text,
            sap_response
        )
        
        if not success:
            log_entry.status = "error"
            log_entry.llm_final_response = beautified_response
            db.add(log_entry)
            db.commit()
            
            return QueryResponse(
                success=False,
                message=f"结果美化失败: {beautified_response}"
            )
        
        log_entry.llm_final_response = beautified_response
        log_entry.status = "success"
        
        # 保存日志
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return QueryResponse(
            success=True,
            message="查询成功",
            order_id=order_id,
            sap_status=sap_response.get("status"),
            final_response=beautified_response,
            log_id=log_entry.id
        )
        
    except Exception as e:
        log_entry.status = "error"
        db.add(log_entry)
        db.commit()
        
        return QueryResponse(
            success=False,
            message=f"查询处理异常: {str(e)}"
        )


@app.get("/api/logs/{user_id}")
def get_user_logs(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的查询历史日志
    
    Args:
        user_id: 用户 ID
        db: 数据库会话
        
    Returns:
        日志列表
    """
    
    logs = db.query(QueryLog).filter(QueryLog.user_id == user_id).order_by(
        QueryLog.timestamp.desc()
    ).limit(20).all()
    
    return {
        "user_id": user_id,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "raw_query": log.raw_query,
                "order_id": json.loads(log.llm_extracted_intent).get("order_id") if log.llm_extracted_intent else None,
                "status": log.status
            }
            for log in logs
        ]
    }


@app.get("/")
def root():
    """根路由 - API 信息"""
    return {
        "status": "running",
        "message": "SAP Query API",
        "version": "1.0.0",
        "endpoints": {
            "login": "POST /api/login",
            "query": "POST /api/query",
            "logs": "GET /api/logs/{user_id}",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "SAP Query API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
