"""
数据库模型定义
包含：用户表、查询日志表
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 获取数据库 URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sap_query_demo.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 创建 Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # 实际项目应使用 bcrypt 加密
    email = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    """查询日志表 - 用于运维审计和准确性追踪"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_query = Column(Text, nullable=False)  # 用户原始输入
    llm_extracted_intent = Column(Text, nullable=True)  # LLM 提取的意图和订单号
    sap_raw_response = Column(Text, nullable=True)  # SAP 返回的原始数据
    llm_final_response = Column(Text, nullable=True)  # LLM 美化后的最终回复
    status = Column(String(20), default="success")  # success, error, timeout


# 创建所有表
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️  数据库初始化警告: {e}")
    print("✅ 继续启动应用，表可能已存在或数据库配置有问题")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
