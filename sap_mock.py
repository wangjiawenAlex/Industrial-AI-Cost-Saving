from typing import Dict, Any
import json

def query_sap_order_status(order_id: str) -> Dict[str, Any]:
    response = {
        "order_id": order_id,
        "status": "制作中",
        "status_code": "02",
        "progress_percentage": 50,
        "details": "订单正在生产中，预计还需要 2-3 天完成",
        "last_update": "2026-01-21 10:30:00",
        "created_date": "2026-01-15",
        "expected_completion": "2026-01-24"
    }
    
    return response


def validate_order_id(order_id: str) -> bool:
    if not order_id:
        return False

    if len(order_id) >= 8 and order_id.isdigit():
        return True

    return False
