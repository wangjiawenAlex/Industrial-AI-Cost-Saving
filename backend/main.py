"""
SAP 订单查询后端 - P0 生产级改造
- PostgreSQL 数据库（支持并发）
- JWT 认证
- Redis 缓存
- API 限流
"""
import hashlib
import json
import logging
import os
from datetime import timedelta
from functools import lru_cache
from typing import Optional

import redis
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from llm_handler import LLMHandler
from models import (
    Base, BusinessData, QueryLog, SessionLocal, User, engine, get_db,
    get_password_hash, verify_access_token, create_access_token, init_db
)
from sap_mock import query_sap_order_status, validate_order_id

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SAP Query API", version="3.0.0-production")

# CORS 配置 - 生产环境应限制来源
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流配置 - 每人 60 次/分钟
limiter = Limiter(key_func=get_remote_address)
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Redis 缓存
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis 连接成功")
except Exception as e:
    logger.warning(f"⚠️  Redis 连接失败: {e}, 缓存功能将不可用")
    redis_client = None

# 安全认证
security = HTTPBearer()

# 请求模型
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user_id: Optional[int] = None
    username: Optional[str] = None


class QueryRequest(BaseModel):
    query_text: str


class QueryResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[str] = None
    sap_status: Optional[str] = None
    final_response: Optional[str] = None
    log_id: Optional[int] = None


# LLM 处理器
try:
    llm_handler = LLMHandler()
except ValueError as exc:
    logger.warning("LLM 未初始化: %s", exc)
    llm_handler = None


def get_cache_key(prefix: str, *args) -> str:
    """生成缓存键"""
    key_str = ":".join(str(a) for a in args)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()[:16]
    return f"sap:{prefix}:{key_hash}"


def get_llm_cache(query: str) -> Optional[str]:
    """获取 LLM 缓存"""
    if not redis_client:
        return None
    try:
        cache_key = get_cache_key("llm", query[:100])
        cached = redis_client.get(cache_key)
        if cached:
            logger.info(f"✅ 缓存命中: {cache_key}")
            return cached
    except Exception as e:
        logger.warning(f"⚠️  缓存读取失败: {e}")
    return None


def set_llm_cache(query: str, response: str, ttl: int = 3600):
    """设置 LLM 缓存（默认1小时）"""
    if not redis_client:
        return
    try:
        cache_key = get_cache_key("llm", query[:100])
        redis_client.setex(cache_key, ttl, response)
    except Exception as e:
        logger.warning(f"⚠️  缓存写入失败: {e}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """验证 JWT Token 并获取当前用户"""
    token = credentials.credentials
    payload = verify_access_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")
    
    return user


def seed_business_data(db: Session) -> None:
    """初始化业务数据"""
    if db.query(BusinessData).count() > 0:
        return

    records = [
        BusinessData(
            order_id="4200000001",
            customer_name="Schneider Electric",
            status="制作中",
            status_code="02",
            progress_percentage=50,
            details="订单正在生产中，预计还需要 2-3 天完成",
            last_update="2026-01-21 10:30:00",
            expected_completion="2026-01-24",
        ),
        BusinessData(
            order_id="4200000002",
            customer_name="Schneider Electric",
            status="已完成",
            status_code="03",
            progress_percentage=100,
            details="订单已完成并进入待发运状态",
            last_update="2026-01-20 15:00:00",
            expected_completion="2026-01-20",
        ),
    ]
    db.add_all(records)
    db.commit()


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    init_db()
    db = SessionLocal()
    try:
        seed_business_data(db)
    finally:
        db.close()
    logger.info("✅ SAP Query API 启动完成 (生产模式)")


@app.post("/api/login", response_model=LoginResponse)
@limiter.limit("60/minute")
def login(request: Request, login_req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录 - 返回 JWT Token"""
    user = db.query(User).filter(User.username == login_req.username).first()

    if not user:
        # 新用户注册
        try:
            new_user = User(
                username=login_req.username,
                password_hash=get_password_hash(login_req.password)
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # 生成 Token
            access_token = create_access_token(
                data={"user_id": new_user.id, "username": new_user.username}
            )
            
            return LoginResponse(
                success=True,
                message="新用户已创建",
                access_token=access_token,
                user_id=new_user.id,
                username=new_user.username
            )
        except IntegrityError:
            return LoginResponse(success=False, message="用户名已存在")
    
    # 验证密码
    if not user.check_password(login_req.password):
        return LoginResponse(success=False, message="密码错误")
    
    if not user.is_active:
        return LoginResponse(success=False, message="用户已被禁用")
    
    # 生成 Token
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return LoginResponse(
        success=True,
        message="登录成功",
        access_token=access_token,
        user_id=user.id,
        username=user.username
    )


@app.post("/api/query", response_model=QueryResponse)
@limiter.limit("60/minute")
def process_query(
    request: Request,
    query_req: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """处理订单查询 - 需要 JWT 认证"""
    log_entry = QueryLog(user_id=current_user.id, raw_query=query_req.query_text)

    try:
        if not llm_handler:
            log_entry.status = "error"
            log_entry.error_message = "LLM 服务未初始化"
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message="LLM 服务未初始化")

        # 1. 意图识别（带缓存）
        cache_key_intent = get_cache_key("intent", query_req.query_text[:100])
        ok = True
        
        if redis_client:
            cached_intent = redis_client.get(cache_key_intent)
            if cached_intent:
                intent_result = json.loads(cached_intent)
                logger.info("✅ 意图缓存命中")
            else:
                ok, intent_result = llm_handler.extract_intent(query_req.query_text)
                if redis_client and ok:
                    redis_client.setex(cache_key_intent, 3600, json.dumps(intent_result))
        else:
            ok, intent_result = llm_handler.extract_intent(query_req.query_text)
        
        log_entry.llm_extracted_intent = json.dumps(intent_result, ensure_ascii=False)

        if not ok:
            log_entry.status = "error"
            log_entry.error_message = intent_result.get("error", "意图识别失败")
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message=f"意图识别失败: {log_entry.error_message}")

        # 2. 提取订单号
        order_id = intent_result.get("order_id", "").strip()
        if not validate_order_id(order_id):
            log_entry.status = "error"
            log_entry.error_message = "无法识别有效订单号"
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message="无法识别有效订单号")

        log_entry.order_id = order_id

        # 3. 查询 SAP（带缓存）
        cache_key_sap = get_cache_key("sap", order_id)
        
        if redis_client:
            cached_sap = redis_client.get(cache_key_sap)
            if cached_sap:
                sap_response = json.loads(cached_sap)
                logger.info("✅ SAP 数据缓存命中")
            else:
                sap_response = query_sap_order_status(db, order_id)
                redis_client.setex(cache_key_sap, 3600, json.dumps(sap_response))
        else:
            sap_response = query_sap_order_status(db, order_id)
        
        log_entry.business_raw_response = json.dumps(sap_response, ensure_ascii=False)

        # 4. 结果美化（带缓存）
        cached_llm = get_llm_cache(query_req.query_text + order_id)
        if cached_llm:
            beautified_response = cached_llm
        else:
            ok, beautified_response = llm_handler.beautify_response(
                query_req.query_text, sap_response
            )
            if ok:
                set_llm_cache(query_req.query_text + order_id, beautified_response)
        
        if not ok:
            log_entry.status = "error"
            log_entry.error_message = beautified_response
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message=f"结果美化失败: {beautified_response}")

        # 5. 记录日志
        log_entry.status = "success"
        log_entry.llm_final_response = beautified_response
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        return QueryResponse(
            success=True,
            message="查询成功",
            order_id=order_id,
            sap_status=sap_response.get("status"),
            final_response=beautified_response,
            log_id=log_entry.id,
        )

    except Exception as exc:
        logger.exception("查询处理失败")
        log_entry.status = "error"
        log_entry.error_message = str(exc)
        db.add(log_entry)
        db.commit()
        return QueryResponse(success=False, message=f"查询处理异常: {exc}")


@app.get("/api/logs")
@limiter.limit("60/minute")
def get_user_logs(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的查询日志"""
    logs = (
        db.query(QueryLog)
        .filter(QueryLog.user_id == current_user.id)
        .order_by(QueryLog.timestamp.desc())
        .limit(20)
        .all()
    )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "raw_query": log.raw_query,
                "order_id": log.order_id,
                "status": log.status,
                "error_message": log.error_message,
            }
            for log in logs
        ],
    }


@app.get("/api/user/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "SAP Query API",
        "version": "3.0.0-production",
        "features": {
            "auth": "JWT",
            "database": "PostgreSQL",
            "cache": "Redis",
            "rate_limit": "60/minute"
        },
        "endpoints": {
            "login": "POST /api/login",
            "query": "POST /api/query (需要 JWT)",
            "logs": "GET /api/logs (需要 JWT)",
            "me": "GET /api/user/me (需要 JWT)",
            "health": "GET /health",
            "docs": "GET /docs",
        },
    }


@app.get("/health")
def health_check():
    """健康检查"""
    from sqlalchemy import text
    health = {"status": "ok", "version": "3.0.0-production"}
    
    # 检查数据库
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health["database"] = "ok"
    except Exception as e:
        health["database"] = f"error: {e}"
    
    # 检查 Redis
    if redis_client:
        try:
            redis_client.ping()
            health["cache"] = "ok"
        except Exception as e:
            health["cache"] = f"error: {e}"
    else:
        health["cache"] = "disabled"
    
    return health


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
        port=int(os.getenv("FASTAPI_PORT", "8000")),
        reload=False,
    )
