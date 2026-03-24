from typing import Any, Dict

from sqlalchemy.orm import Session

from models import BusinessData, SessionLocal


def query_sap_order_status(db: Session, order_id: str) -> Dict[str, Any]:
    """从真实数据库查询订单状态"""
    record = db.query(BusinessData).filter(BusinessData.order_id == order_id).first()
    if record:
        return {
            "order_id": record.order_id,
            "customer_name": record.customer_name,
            "status": record.status,
            "status_code": record.status_code,
            "progress_percentage": record.progress_percentage,
            "details": record.details,
            "last_update": record.last_update,
            "expected_completion": record.expected_completion,
            "source": "sqlite_db",
        }

    # 订单不存在
    return {
        "order_id": order_id,
        "status": "未找到",
        "status_code": "00",
        "progress_percentage": 0,
        "details": f"系统中未找到订单号 {order_id} 的记录",
        "last_update": "",
        "expected_completion": "",
        "source": "not_found",
    }


def validate_order_id(order_id: str) -> bool:
    if not order_id:
        return False
    return len(order_id) >= 8 and order_id.isdigit()
