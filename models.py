from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sap_query_demo.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_query = Column(Text, nullable=False)
    llm_extracted_intent = Column(Text, nullable=True)
    sap_raw_response = Column(Text, nullable=True)
    llm_final_response = Column(Text, nullable=True)
    status = Column(String(20), default="success")


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️  数据库初始化警告: {e}")
    print("✅ 继续启动应用，表可能已存在或数据库配置有问题")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
