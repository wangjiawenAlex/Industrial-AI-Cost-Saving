from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import logging
import os

from llm_handler import LLMHandler
from models import Base, BusinessData, QueryLog, SessionLocal, User, engine, get_db
from sap_mock import query_sap_order_status, validate_order_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SAP Query API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: int | None = None


class QueryRequest(BaseModel):
    user_id: int
    query_text: str


class QueryResponse(BaseModel):
    success: bool
    message: str
    order_id: str | None = None
    sap_status: str | None = None
    final_response: str | None = None
    log_id: int | None = None


try:
    llm_handler = LLMHandler()
except ValueError as exc:
    logger.warning("LLM 未初始化: %s", exc)
    llm_handler = None


def seed_business_data(db: Session) -> None:
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
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_business_data(db)
    finally:
        db.close()


@app.post("/api/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        new_user = User(username=request.username, password=request.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return LoginResponse(success=True, message="新用户已创建", user_id=new_user.id)

    if user.password != request.password:
        return LoginResponse(success=False, message="密码错误")

    return LoginResponse(success=True, message="登录成功", user_id=user.id)


@app.post("/api/query", response_model=QueryResponse)
def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    log_entry = QueryLog(user_id=request.user_id, raw_query=request.query_text)

    try:
        if not llm_handler:
            log_entry.status = "error"
            log_entry.error_message = "LLM 服务未初始化"
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message="LLM 服务未初始化，请检查 DEEPSEEK_API_KEY")

        ok, intent_result = llm_handler.extract_intent(request.query_text)
        log_entry.llm_extracted_intent = json.dumps(intent_result, ensure_ascii=False)

        if not ok:
            log_entry.status = "error"
            log_entry.error_message = intent_result.get("error", "意图识别失败")
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message=f"意图识别失败: {log_entry.error_message}")

        order_id = intent_result.get("order_id", "").strip()
        if not validate_order_id(order_id):
            log_entry.status = "error"
            log_entry.error_message = "无法识别有效订单号"
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message="无法识别有效订单号")

        log_entry.order_id = order_id
        sap_response = query_sap_order_status(db, order_id)
        log_entry.business_raw_response = json.dumps(sap_response, ensure_ascii=False)

        ok, beautified_response = llm_handler.beautify_response(request.query_text, sap_response)
        if not ok:
            log_entry.status = "error"
            log_entry.error_message = beautified_response
            db.add(log_entry)
            db.commit()
            return QueryResponse(success=False, message=f"结果美化失败: {beautified_response}")

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

    except Exception as exc:  # noqa: BLE001
        logger.exception("查询处理失败")
        log_entry.status = "error"
        log_entry.error_message = str(exc)
        db.add(log_entry)
        db.commit()
        return QueryResponse(success=False, message=f"查询处理异常: {exc}")


@app.get("/api/logs/{user_id}")
def get_user_logs(user_id: int, db: Session = Depends(get_db)):
    logs = (
        db.query(QueryLog)
        .filter(QueryLog.user_id == user_id)
        .order_by(QueryLog.timestamp.desc())
        .limit(20)
        .all()
    )

    return {
        "user_id": user_id,
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


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "SAP Query API",
        "version": "2.0.0",
        "endpoints": {
            "login": "POST /api/login",
            "query": "POST /api/query",
            "logs": "GET /api/logs/{user_id}",
            "health": "GET /health",
            "docs": "GET /docs",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "SAP Query API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend:app",
        host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
        port=int(os.getenv("FASTAPI_PORT", "8000")),
        reload=False,
    )
