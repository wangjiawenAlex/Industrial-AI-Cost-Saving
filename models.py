from datetime import datetime
import os

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://sap_user:sap_pass@postgres:5432/sap_demo",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    query_logs = relationship("QueryLog", back_populates="user")


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


try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    print(f"⚠️  数据库初始化警告: {exc}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
