"""
SAP 模拟模块
目前所有查询都返回"制作中"状态
"""

from typing import Dict, Any
import json


def query_sap_order_status(order_id: str) -> Dict[str, Any]:
    """
    模拟 SAP 查询接口
    
    Args:
        order_id: 订单号
        
    Returns:
        包含订单信息的字典
    """
    
    # 硬编码返回"制作中"
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
    """
    验证订单号格式
    公司订单号格式：4 位数字开头 (如 4200000001)
    
    Args:
        order_id: 待验证的订单号
        
    Returns:
        是否有效
    """
    if not order_id:
        return False
    
    # 简单的格式验证：8-10 位数字
    if len(order_id) >= 8 and order_id.isdigit():
        return True
    
    return False
