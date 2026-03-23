"""
数据模型 - PostgreSQL + 密码哈希
P0 改造：支持并发、安全认证
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sap_user:sap_pass123@localhost:5432/sap_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,          # 连接池大小
    max_overflow=20,       # 允许超出的连接数
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    is_active = Column(Integer, default=1)  # 1=启用, 0=禁用
    created_at = Column(DateTime, default=datetime.utcnow)

    query_logs = relationship("QueryLog", back_populates="user")

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)


class BusinessData(Base):
    __tablename__ = "business_data"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(20), unique=True, index=True, nullable=False)
    customer_name = Column(String(100), nullable=True)
    status = Column(String(30), nullable=False)
    status_code = Column(String(10), nullable=True)
    progress_percentage = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    expected_completion = Column(String(30), nullable=True)
    last_update = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_query = Column(Text, nullable=False)
    order_id = Column(String(20), nullable=True)
    llm_extracted_intent = Column(Text, nullable=True)
    business_raw_response = Column(Text, nullable=True)
    llm_final_response = Column(Text, nullable=True)
    status = Column(String(20), default="success")
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="query_logs")


# 初始化数据库表
def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWT 配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    from jose import jwt
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[dict]:
    """验证 JWT Token"""
    from jose import jwt, JWTError
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
