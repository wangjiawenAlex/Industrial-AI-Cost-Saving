"""
数据迁移脚本：SQLite → PostgreSQL
将旧版本的业务数据迁移到新的 PostgreSQL 数据库
"""
import os
import sqlite3
from datetime import datetime

# SQLite 数据库路径
SQLITE_DB = os.path.join(os.path.dirname(__file__), "sap_data.db")

# PostgreSQL 连接
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sap_user:sap_pass123@localhost:5432/sap_db"
)


def get_sqlite_conn():
    return sqlite3.connect(SQLITE_DB)


def migrate_users(sqlite_conn, pg_conn):
    """迁移用户（密码需要重新哈希）"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # 获取旧用户
    sqlite_cursor.execute("SELECT id, username, password, email, created_at FROM users")
    users = sqlite_cursor.fetchall()
    
    from models import get_password_hash
    
    for user in users:
        old_id, username, password, email, created_at = user
        # 旧密码是明文，需要重新哈希
        password_hash = get_password_hash(password)
        
        try:
            pg_cursor.execute(
                """
                INSERT INTO users (username, password_hash, email, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
                """,
                (username, password_hash, email, 1, created_at)
            )
            print(f"✅ 迁移用户: {username}")
        except Exception as e:
            print(f"❌ 迁移用户失败 {username}: {e}")
    
    pg_conn.commit()


def migrate_business_data(sqlite_conn, pg_conn):
    """迁移业务数据（订单）"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM business_data")
    records = sqlite_cursor.fetchall()
    
    # 获取列名
    columns = [desc[0] for desc in sqlite_cursor.description]
    
    for record in records:
        data = dict(zip(columns, record))
        
        try:
            pg_cursor.execute(
                """
                INSERT INTO business_data 
                (order_id, customer_name, status, status_code, progress_percentage, 
                 details, expected_completion, last_update, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING
                """,
                (
                    data.get('order_id'),
                    data.get('customer_name'),
                    data.get('status'),
                    data.get('status_code'),
                    data.get('progress_percentage'),
                    data.get('details'),
                    data.get('expected_completion'),
                    data.get('last_update'),
                    data.get('created_at') or datetime.utcnow()
                )
            )
        except Exception as e:
            print(f"❌ 迁移订单失败 {data.get('order_id')}: {e}")
    
    pg_conn.commit()
    print(f"✅ 迁移 {len(records)} 条订单数据")


def migrate_query_logs(sqlite_conn, pg_conn):
    """迁移查询日志"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM query_logs")
    records = sqlite_cursor.fetchall()
    
    columns = [desc[0] for desc in sqlite_cursor.description]
    
    for record in records:
        data = dict(zip(columns, record))
        
        try:
            pg_cursor.execute(
                """
                INSERT INTO query_logs
                (user_id, timestamp, raw_query, order_id, llm_extracted_intent,
                 business_raw_response, llm_final_response, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data.get('user_id'),
                    data.get('timestamp'),
                    data.get('raw_query'),
                    data.get('order_id'),
                    data.get('llm_extracted_intent'),
                    data.get('business_raw_response'),
                    data.get('llm_final_response'),
                    data.get('status'),
                    data.get('error_message')
                )
            )
        except Exception as e:
            print(f"❌ 迁移日志失败: {e}")
    
    pg_conn.commit()
    print(f"✅ 迁移 {len(records)} 条日志")


def main():
    from sqlalchemy import create_engine
    
    print("🔄 开始数据迁移: SQLite → PostgreSQL")
    
    # 连接 SQLite
    sqlite_conn = get_sqlite_conn()
    
    # 连接 PostgreSQL
    pg_engine = create_engine(DATABASE_URL)
    pg_conn = pg_engine.connect()
    
    try:
        # 迁移数据
        migrate_users(sqlite_conn, pg_conn)
        migrate_business_data(sqlite_conn, pg_conn)
        migrate_query_logs(sqlite_conn, pg_conn)
        
        print("\n🎉 数据迁移完成!")
        
    finally:
        sqlite_conn.close()
        pg_conn.close()
        pg_engine.dispose()


if __name__ == "__main__":
    main()
