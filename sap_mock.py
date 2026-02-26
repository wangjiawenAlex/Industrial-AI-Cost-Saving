from typing import Any, Dict

from sqlalchemy.orm import Session

from models import BusinessData


def query_sap_order_status(db: Session, order_id: str) -> Dict[str, Any]:
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
        }

    return {
        "order_id": order_id,
        "status": "制作中",
        "status_code": "02",
        "progress_percentage": 50,
        "details": "订单正在生产中，预计还需要 2-3 天完成",
        "last_update": "2026-01-21 10:30:00",
        "expected_completion": "2026-01-24",
        "source": "mock_fallback",
    }


def validate_order_id(order_id: str) -> bool:
    if not order_id:
        return False
    return len(order_id) >= 8 and order_id.isdigit()
