import json
from typing import Any


def build_intent_prompt(user_input: str) -> str:
    return f"""
你是企业审批助手。请判断下面文本属于哪种流程，只能返回 JSON。

候选流程：
- leave: 请假
- reimbursement: 报销
- purchase: 采购

返回格式：
{{
  "process_type": "leave | reimbursement | purchase",
  "confidence": 0.95
}}

用户输入：
{user_input}
""".strip()


def build_extraction_prompt(user_input: str, process_type: str) -> str:
    schema_map = {
        "leave": {
            "leave_type": "string",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "days": "number",
            "reason": "string",
            "handover_person": "string",
        },
        "reimbursement": {
            "reimbursement_type": "string",
            "amount": "number",
            "expense_date": "YYYY-MM-DD",
            "reason": "string",
            "invoice_no": "string",
        },
        "purchase": {
            "item_name": "string",
            "quantity": "number",
            "unit_price": "number",
            "total_amount": "number",
            "purpose": "string",
            "supplier": "string",
        },
    }
    schema_text = json.dumps(schema_map[process_type], ensure_ascii=False, indent=2)
    return f"""
你是信息抽取助手。请从用户文本中抽取 {process_type} 流程需要的字段。
只返回 JSON，不要添加解释，不要编造未知信息。
无法确定的字段请省略。

字段规范：
{schema_text}

用户输入：
{user_input}
""".strip()


def build_summary_prompt(payload: dict[str, Any]) -> str:
    return f"""
你是审批摘要助手。请基于下面数据返回 JSON，字段固定为 title 和 summary，使用中文。
title 要简洁，summary 要概括关键信息、审批链路、缺失字段和风险提示。

输入数据：
{json.dumps(payload, ensure_ascii=False, indent=2)}

返回格式：
{{
  "title": "字符串",
  "summary": "字符串"
}}
""".strip()
