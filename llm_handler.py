"""
LLM 处理模块
使用 DeepSeek API 进行：
1. 意图识别（提取订单号）
2. 结果美化（组织最终回复）
"""

import os
import json
import requests
from typing import Dict, Any, Tuple
from pydantic import BaseModel, ValidationError


class IntentExtractionResult(BaseModel):
    """意图提取结果的数据模型"""
    order_id: str
    query_type: str  # "status_query" 或 "other"
    confidence: float


class LLMHandler:
    """LLM 处理器"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
    
    def extract_intent(self, user_query: str) -> Tuple[bool, Dict[str, Any]]:
        """
        使用 LLM 从用户查询中提取意图和订单号
        
        Args:
            user_query: 用户的自然语言查询
            
        Returns:
            (成功标志, 提取结果字典)
        """
        
        system_prompt = """你是一个 SAP 订单查询助手。你的任务是从用户的自然语言查询中提取以下信息：
1. 订单号（order_id）：通常是 8-10 位数字
2. 查询类型（query_type）：可能是 "status_query"（查询状态）或 "other"（其他）

请以 JSON 格式返回结果，格式如下：
{
    "order_id": "提取到的订单号，如果没有则为空字符串",
    "query_type": "status_query 或 other",
    "confidence": 0.0 到 1.0 之间的置信度
}

重要：只返回 JSON，不要包含其他文本。"""
        
        user_message = f"请从以下查询中提取订单号和查询类型：\n{user_query}"
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 200
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return False, {"error": f"API 返回错误: {response.status_code}"}
            
            result = response.json()
            
            # 提取 LLM 的回复
            if "choices" not in result or len(result["choices"]) == 0:
                return False, {"error": "API 返回格式错误"}
            
            llm_response = result["choices"][0]["message"]["content"].strip()
            
            # 解析 JSON
            try:
                extracted = json.loads(llm_response)
                return True, extracted
            except json.JSONDecodeError:
                return False, {"error": f"LLM 返回的不是有效 JSON: {llm_response}"}
                
        except requests.exceptions.Timeout:
            return False, {"error": "API 请求超时"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def beautify_response(self, user_query: str, sap_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        使用 LLM 美化 SAP 返回的数据，生成友好的中文回复
        
        Args:
            user_query: 用户的原始查询
            sap_data: SAP 返回的原始数据
            
        Returns:
            (成功标志, 美化后的回复文本)
        """
        
        system_prompt = """你是一个 SAP 订单查询助手。你的任务是根据 SAP 系统返回的订单数据，
生成一个友好、清晰的中文回复。

重要规则：
1. 所有信息必须基于提供的 SAP 数据，不得编造任何信息
2. 使用简洁、易懂的语言
3. 如果状态是"制作中"，要说明进度百分比和预计完成时间
4. 回复应该直接回答用户的问题"""
        
        sap_data_str = json.dumps(sap_data, ensure_ascii=False, indent=2)
        user_message = f"""用户查询：{user_query}

SAP 系统返回的数据：
{sap_data_str}

请根据上述数据生成一个友好的中文回复。"""
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return False, f"API 返回错误: {response.status_code}"
            
            result = response.json()
            
            if "choices" not in result or len(result["choices"]) == 0:
                return False, "API 返回格式错误"
            
            beautified_response = result["choices"][0]["message"]["content"].strip()
            return True, beautified_response
            
        except requests.exceptions.Timeout:
            return False, "API 请求超时，请稍后重试"
        except Exception as e:
            return False, f"处理失败: {str(e)}"
