from __future__ import annotations

from datetime import timedelta
import re
from typing import Any

from app.utils.helpers import ROLE_LABELS, determine_approval_route, now_shanghai


LEAVE_TYPES = ["事假", "病假", "年假", "婚假", "产假", "丧假"]
REIMBURSEMENT_KEYWORDS = {
    "差旅": ["差旅", "出差", "住宿", "酒店"],
    "餐饮": ["餐饮", "吃饭", "用餐"],
    "交通": ["交通", "打车", "高铁", "机票", "火车"],
    "办公用品": ["办公用品", "文具", "纸张", "打印耗材"],
    "通讯": ["通讯", "电话费", "网费", "通信"],
}


def classify_intent(text: str) -> tuple[str, float]:
    lowered = text.lower()
    if re.search(r"采购|购买|购置|订购", text):
        return "purchase", 0.97
    if re.search(r"报销|发票|费用| reimbursement", lowered):
        return "reimbursement", 0.94
    if re.search(r"请假|休假|调休|病假|年假|婚假|产假|丧假", text):
        return "leave", 0.95
    return "leave", 0.55


def parse_date_range(text: str) -> tuple[str | None, str | None]:
    today = now_shanghai().date()

    full_match = re.search(
        r"(\d{4}-\d{1,2}-\d{1,2})\s*(?:到|至|-|~)\s*(\d{4}-\d{1,2}-\d{1,2})",
        text,
    )
    if full_match:
        return full_match.group(1), full_match.group(2)

    month_day_match = re.search(
        r"(\d{1,2})月(\d{1,2})[号日]?\s*(?:到|至|-|~)\s*(?:(\d{1,2})月)?(\d{1,2})[号日]?",
        text,
    )
    if month_day_match:
        start_month = int(month_day_match.group(1))
        start_day = int(month_day_match.group(2))
        end_month = int(month_day_match.group(3) or start_month)
        end_day = int(month_day_match.group(4))
        start_date = f"{today.year:04d}-{start_month:02d}-{start_day:02d}"
        end_date = f"{today.year:04d}-{end_month:02d}-{end_day:02d}"
        return start_date, end_date

    return None, None


def parse_single_date(text: str) -> str | None:
    today = now_shanghai().date()
    full_match = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", text)
    if full_match:
        return full_match.group(1)

    month_day_match = re.search(r"(\d{1,2})月(\d{1,2})[号日]?", text)
    if month_day_match:
        month = int(month_day_match.group(1))
        day = int(month_day_match.group(2))
        return f"{today.year:04d}-{month:02d}-{day:02d}"

    if "上周" in text:
        return (today - timedelta(days=7)).strftime("%Y-%m-%d")
    if "昨天" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    if "今天" in text:
        return today.strftime("%Y-%m-%d")
    return None


def extract_leave_fields(text: str) -> dict[str, Any]:
    start_date, end_date = parse_date_range(text)
    fields: dict[str, Any] = {}
    leave_type = next((item for item in LEAVE_TYPES if item in text), "事假")
    fields["leave_type"] = leave_type
    if start_date:
        fields["start_date"] = start_date
    if end_date:
        fields["end_date"] = end_date

    days_match = re.search(r"(\d+(?:\.\d+)?)\s*天", text)
    if days_match:
        fields["days"] = float(days_match.group(1))

    handover_match = re.search(r"交接(?:给|人(?:是|为)?)\s*([A-Za-z0-9\u4e00-\u9fa5]{2,20})", text)
    if handover_match:
        fields["handover_person"] = handover_match.group(1).strip("，。,. ")

    reason_match = re.search(r"(?:因为|由于|原因是|原因[:：])(.+?)(?:[，。,.]|$)", text)
    if reason_match:
        fields["reason"] = reason_match.group(1).strip()
    return fields


def extract_reimbursement_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    reimburse_type = "其他"
    for label, keywords in REIMBURSEMENT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            reimburse_type = label
            break
    fields["reimbursement_type"] = reimburse_type

    amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:元|块)", text)
    if amount_match:
        fields["amount"] = float(amount_match.group(1))

    expense_date = parse_single_date(text)
    if expense_date:
        fields["expense_date"] = expense_date

    reason_match = re.search(r"(?:因为|用于|事由(?:是|为)?|花了)(.+?)(?:需要报销|，|。|$)", text)
    if reason_match:
        fields["reason"] = reason_match.group(1).strip("，。,. ")
    elif reimburse_type != "其他":
        fields["reason"] = f"{reimburse_type}费用"

    invoice_match = re.search(r"(?:发票(?:号码|号)?(?:是|为)?\s*)([A-Za-z0-9-]+)", text)
    if invoice_match:
        fields["invoice_no"] = invoice_match.group(1)
    return fields


def extract_purchase_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}

    quantity_item_match = re.search(
        r"(?:采购|购买|购置)(\d+(?:\.\d+)?)\s*([台个件套张箱支把])?([A-Za-z0-9\u4e00-\u9fa5]+)",
        text,
    )
    if quantity_item_match:
        fields["quantity"] = float(quantity_item_match.group(1))
        fields["item_name"] = quantity_item_match.group(3).strip()
    else:
        fallback_match = re.search(r"(\d+(?:\.\d+)?)\s*([台个件套张箱支把])([A-Za-z0-9\u4e00-\u9fa5]+)", text)
        if fallback_match:
            fields["quantity"] = float(fallback_match.group(1))
            fields["item_name"] = fallback_match.group(3).strip()

    unit_price_match = re.search(r"单价\s*(\d+(?:\.\d+)?)\s*(?:元|块)", text)
    if unit_price_match:
        fields["unit_price"] = float(unit_price_match.group(1))

    total_amount_match = re.search(r"(?:总共|总计|总金额)\s*(\d+(?:\.\d+)?)\s*(?:元|块)", text)
    if total_amount_match:
        fields["total_amount"] = float(total_amount_match.group(1))

    purpose_match = re.search(r"用于(.+?)(?:[，。,.]|$)", text)
    if purpose_match:
        fields["purpose"] = purpose_match.group(1).strip()

    supplier_match = re.search(r"供应商(?:是|为)?\s*([A-Za-z0-9\u4e00-\u9fa5]+)", text)
    if supplier_match:
        fields["supplier"] = supplier_match.group(1).strip("，。,. ")

    if "quantity" in fields and "unit_price" in fields and "total_amount" not in fields:
        fields["total_amount"] = round(float(fields["quantity"]) * float(fields["unit_price"]), 2)
    return fields


def extract_entities(text: str, process_type: str) -> dict[str, Any]:
    if process_type == "leave":
        return extract_leave_fields(text)
    if process_type == "reimbursement":
        return extract_reimbursement_fields(text)
    return extract_purchase_fields(text)


def get_missing_fields(process_type: str, extracted_fields: dict[str, Any]) -> list[str]:
    required_map = {
        "leave": ["leave_type", "start_date", "end_date", "days", "reason", "handover_person"],
        "reimbursement": ["reimbursement_type", "amount", "expense_date", "reason"],
        "purchase": ["item_name", "quantity", "unit_price", "total_amount", "purpose"],
    }
    return [
        field
        for field in required_map[process_type]
        if extracted_fields.get(field) in (None, "", [])
    ]


def generate_title(process_type: str, extracted_fields: dict[str, Any]) -> str:
    if process_type == "leave":
        leave_type = extracted_fields.get("leave_type", "请假")
        days = extracted_fields.get("days")
        return f"{leave_type}申请-{int(days) if days else '待补充'}天"
    if process_type == "reimbursement":
        reimbursement_type = extracted_fields.get("reimbursement_type", "报销")
        amount = extracted_fields.get("amount")
        return f"{reimbursement_type}报销-{int(amount) if amount else '待补充'}元"
    item_name = extracted_fields.get("item_name", "物品")
    quantity = extracted_fields.get("quantity")
    quantity_text = int(quantity) if isinstance(quantity, (int, float)) and float(quantity).is_integer() else quantity
    return f"采购申请-{item_name}{quantity_text or ''}件"


def generate_summary(
    process_type: str,
    extracted_fields: dict[str, Any],
    missing_fields: list[str],
    required_materials: list[str],
    approval_route: list[str],
    risk_tips: list[str],
) -> str:
    route_text = "、".join(ROLE_LABELS.get(role, role) for role in approval_route)
    missing_text = "无" if not missing_fields else "、".join(missing_fields)
    material_text = "无" if not required_materials else "、".join(required_materials)
    risk_text = "无" if not risk_tips else "；".join(risk_tips)

    if process_type == "leave":
        return (
            f"申请人提交{extracted_fields.get('days', '待补充')}天"
            f"{extracted_fields.get('leave_type', '请假')}申请，"
            f"时间为{extracted_fields.get('start_date', '待补充')}至{extracted_fields.get('end_date', '待补充')}，"
            f"原因为{extracted_fields.get('reason', '待补充')}。"
            f"审批链路为{route_text}，缺失字段：{missing_text}，所需材料：{material_text}，风险提示：{risk_text}。"
        )

    if process_type == "reimbursement":
        return (
            f"申请人提交{extracted_fields.get('reimbursement_type', '报销')}报销，"
            f"金额{extracted_fields.get('amount', '待补充')}元，"
            f"消费日期为{extracted_fields.get('expense_date', '待补充')}，"
            f"报销事由为{extracted_fields.get('reason', '待补充')}。"
            f"审批链路为{route_text}，缺失字段：{missing_text}，所需材料：{material_text}，风险提示：{risk_text}。"
        )

    return (
        f"申请人提交采购申请，采购{extracted_fields.get('item_name', '待补充')}，"
        f"数量{extracted_fields.get('quantity', '待补充')}，"
        f"单价{extracted_fields.get('unit_price', '待补充')}元，"
        f"总金额{extracted_fields.get('total_amount', '待补充')}元。"
        f"审批链路为{route_text}，缺失字段：{missing_text}，所需材料：{material_text}，风险提示：{risk_text}。"
    )
