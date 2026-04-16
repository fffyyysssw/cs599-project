from __future__ import annotations

from datetime import date, datetime
import math
from pathlib import Path
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.user import User


TZ = ZoneInfo("Asia/Shanghai")
SUPPORTED_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}
PROCESS_PREFIX = {"leave": "LV", "reimbursement": "RB", "purchase": "PC"}
PROCESS_LABELS = {"leave": "请假申请", "reimbursement": "报销申请", "purchase": "采购申请"}
ROLE_LABELS = {
    "employee": "员工",
    "manager": "主管",
    "finance": "财务",
    "hr": "HR",
    "procurement": "采购",
    "admin": "管理员",
    "department_head": "部门负责人",
}
MATERIAL_LABELS = {
    "invoice": "发票",
    "sick_leave_certificate": "病假证明",
    "quotation": "报价单",
    "other": "其他材料",
}


def now_shanghai() -> datetime:
    return datetime.now(TZ)


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_process_templates() -> list[dict[str, Any]]:
    return [
        {
            "code": "leave",
            "name": "请假申请",
            "description": "支持事假、病假、年假、婚假、产假、丧假等请假流程。",
            "form_schema": {
                "fields": [
                    {
                        "key": "leave_type",
                        "label": "请假类型",
                        "type": "select",
                        "required": True,
                        "options": ["事假", "病假", "年假", "婚假", "产假", "丧假"],
                    },
                    {"key": "start_date", "label": "开始日期", "type": "date", "required": True},
                    {"key": "end_date", "label": "结束日期", "type": "date", "required": True},
                    {"key": "days", "label": "天数", "type": "number", "required": True, "min": 0.5},
                    {"key": "reason", "label": "请假原因", "type": "textarea", "required": True},
                    {"key": "handover_person", "label": "工作交接人", "type": "text", "required": False},
                ]
            },
            "rules": {
                "approval_rules": [
                    {"max_days": 1, "route": ["manager"]},
                    {"min_days": 1, "max_days": 3, "route": ["manager", "hr"]},
                    {"min_days": 3, "route": ["manager", "department_head", "hr"]},
                ],
                "required_material_rules": [
                    {"leave_type": "病假", "min_days": 2, "material": "sick_leave_certificate"}
                ],
                "supported_types": ["事假", "病假", "年假", "婚假", "产假", "丧假"],
            },
        },
        {
            "code": "reimbursement",
            "name": "报销申请",
            "description": "支持差旅、餐饮、交通、办公用品、通讯等报销场景。",
            "form_schema": {
                "fields": [
                    {
                        "key": "reimbursement_type",
                        "label": "报销类型",
                        "type": "select",
                        "required": True,
                        "options": ["差旅", "餐饮", "交通", "办公用品", "通讯", "其他"],
                    },
                    {"key": "amount", "label": "报销金额(元)", "type": "number", "required": True, "min": 0.01},
                    {"key": "expense_date", "label": "消费日期", "type": "date", "required": True},
                    {"key": "reason", "label": "报销事由", "type": "textarea", "required": True},
                    {"key": "invoice_no", "label": "发票号码", "type": "text", "required": False},
                ]
            },
            "rules": {
                "approval_rules": [
                    {"max_amount": 1000, "route": ["manager"]},
                    {"min_amount": 1000, "max_amount": 5000, "route": ["manager", "finance"]},
                    {"min_amount": 5000, "route": ["manager", "department_head", "finance"]},
                ],
                "required_materials": ["invoice"],
                "supported_types": ["差旅", "餐饮", "交通", "办公用品", "通讯", "其他"],
            },
        },
        {
            "code": "purchase",
            "name": "采购申请",
            "description": "支持办公采购、设备采购、耗材采购等采购流程。",
            "form_schema": {
                "fields": [
                    {"key": "item_name", "label": "采购物品", "type": "text", "required": True},
                    {"key": "quantity", "label": "数量", "type": "number", "required": True, "min": 1},
                    {"key": "unit_price", "label": "单价(元)", "type": "number", "required": True, "min": 0.01},
                    {
                        "key": "total_amount",
                        "label": "总金额(元)",
                        "type": "number",
                        "required": True,
                        "computed": "quantity * unit_price",
                    },
                    {"key": "purpose", "label": "采购用途", "type": "textarea", "required": True},
                    {"key": "supplier", "label": "供应商", "type": "text", "required": False},
                ]
            },
            "rules": {
                "approval_rules": [
                    {"max_amount": 2000, "route": ["manager"]},
                    {"min_amount": 2000, "max_amount": 5000, "route": ["manager", "procurement"]},
                    {
                        "min_amount": 5000,
                        "route": ["manager", "department_head", "procurement", "finance"],
                    },
                ],
                "required_material_rules": [{"min_amount": 3000, "material": "quotation"}],
            },
        },
    ]


def get_required_fields(process_type: str) -> list[str]:
    mapping = {
        "leave": ["leave_type", "start_date", "end_date", "days", "reason"],
        "reimbursement": ["reimbursement_type", "amount", "expense_date", "reason"],
        "purchase": ["item_name", "quantity", "unit_price", "total_amount", "purpose"],
    }
    return mapping[process_type]


def parse_date_string(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def calculate_leave_days(start_date: str, end_date: str) -> float:
    start = parse_date_string(start_date)
    end = parse_date_string(end_date)
    if not start or not end:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请假日期格式错误")
    days = (end - start).days + 1
    if days <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请假天数必须大于0")
    return float(days)


def round_amount(value: Any) -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="金额格式不正确",
        ) from exc
    if amount < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="金额不能为负数")
    return round(amount, 2)


def determine_required_materials(process_type: str, form_data: dict[str, Any]) -> list[str]:
    materials: list[str] = []
    if process_type == "leave":
        leave_type = form_data.get("leave_type")
        days = float(form_data.get("days", 0) or 0)
        if leave_type == "病假" and days > 2:
            materials.append("sick_leave_certificate")
    elif process_type == "reimbursement":
        materials.append("invoice")
    elif process_type == "purchase":
        amount = float(form_data.get("total_amount", 0) or 0)
        if amount > 3000:
            materials.append("quotation")
    return materials


def determine_approval_route(process_type: str, form_data: dict[str, Any]) -> list[str]:
    if process_type == "leave":
        days = float(form_data.get("days", 0) or 0)
        if days <= 1:
            return ["manager"]
        if days <= 3:
            return ["manager", "hr"]
        return ["manager", "department_head", "hr"]

    amount_key = "amount" if process_type == "reimbursement" else "total_amount"
    amount = float(form_data.get(amount_key, 0) or 0)

    if process_type == "reimbursement":
        if amount <= 1000:
            return ["manager"]
        if amount <= 5000:
            return ["manager", "finance"]
        return ["manager", "department_head", "finance"]

    if amount <= 2000:
        return ["manager"]
    if amount <= 5000:
        return ["manager", "procurement"]
    return ["manager", "department_head", "procurement", "finance"]


def build_risk_tips(process_type: str, form_data: dict[str, Any], required_materials: list[str]) -> list[str]:
    tips: list[str] = []
    if process_type == "leave":
        days = float(form_data.get("days", 0) or 0)
        if days > 3:
            tips.append("请假时间超过3天，需要部门负责人参与审批")
        if form_data.get("leave_type") == "病假" and days > 2:
            tips.append("病假超过2天，请上传病假证明")
    elif process_type == "reimbursement":
        amount = float(form_data.get("amount", 0) or 0)
        if amount > 5000:
            tips.append("报销金额超过5000元，需要部门负责人额外审批")
        if "invoice" in required_materials:
            tips.append("报销必须上传发票")
    elif process_type == "purchase":
        amount = float(form_data.get("total_amount", 0) or 0)
        if amount > 5000:
            tips.append("采购金额超过5000元，需要四级审批")
        if "quotation" in required_materials:
            tips.append("采购金额超过3000元，需要上传报价单")
    return tips


def generate_application_no(db: Session, process_type: str) -> str:
    prefix = PROCESS_PREFIX[process_type]
    date_part = now_shanghai().strftime("%Y%m%d")
    like_pattern = f"{prefix}{date_part}%"
    count = db.scalar(select(func.count(Application.id)).where(Application.application_no.like(like_pattern))) or 0
    return f"{prefix}{date_part}{count + 1:03d}"


def resolve_approver(db: Session, role: str, applicant: User) -> User | None:
    stmt = select(User).where(User.is_active.is_(True))
    if role == "manager":
        if applicant.role == "employee":
            manager = db.scalar(
                stmt.where(User.role == "manager", User.department == applicant.department).limit(1)
            )
            if manager:
                return manager
        return db.scalar(stmt.where(User.role == "admin").limit(1))
    if role == "department_head":
        return db.scalar(stmt.where(User.role == "admin").limit(1))
    approver = db.scalar(stmt.where(User.role == role).limit(1))
    if approver:
        return approver
    return db.scalar(stmt.where(User.role == "admin").limit(1))


def user_can_view_application(user: User, application: Application) -> bool:
    if user.role == "admin" or application.applicant_id == user.id:
        return True
    return any(step.approver_id == user.id for step in application.approval_steps)


def user_can_approve_step(user: User, approver_id: int | None, approver_role: str) -> bool:
    if user.role == "admin":
        return True
    if approver_id is not None:
        return approver_id == user.id
    if approver_role == "department_head":
        return user.role == "admin"
    return approver_role == user.role


def normalize_form_data(process_type: str, form_data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(form_data)
    if process_type == "leave":
        normalized["days"] = calculate_leave_days(normalized["start_date"], normalized["end_date"])
    elif process_type == "reimbursement":
        normalized["amount"] = round_amount(normalized["amount"])
    elif process_type == "purchase":
        quantity = float(normalized["quantity"])
        unit_price = round_amount(normalized["unit_price"])
        if quantity <= 0 or unit_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="数量和单价必须大于0",
            )
        normalized["quantity"] = int(quantity) if float(quantity).is_integer() else quantity
        normalized["unit_price"] = unit_price
        normalized["total_amount"] = round(quantity * unit_price, 2)
    return normalized


def validate_required_fields(process_type: str, form_data: dict[str, Any]) -> None:
    missing = [
        field
        for field in get_required_fields(process_type)
        if form_data.get(field) in (None, "", [])
    ]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"缺少必填字段：{', '.join(missing)}",
        )


def validate_required_materials(material_types: list[str], required_materials: list[str]) -> None:
    missing = [item for item in required_materials if item not in material_types]
    if missing:
        labels = [MATERIAL_LABELS.get(item, item) for item in missing]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"缺少必需材料：{', '.join(labels)}",
        )


def build_upload_path(filename: str, upload_root: str | Path) -> tuple[Path, str]:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_FILE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件类型")
    date_dir = now_shanghai().strftime("%Y-%m-%d")
    root = ensure_directory(upload_root)
    target_dir = ensure_directory(root / date_dir)
    file_name = f"{uuid4().hex}{extension}"
    absolute_path = target_dir / file_name
    relative_path = f"uploads/{date_dir}/{file_name}"
    return absolute_path, relative_path


def ceil_division(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if page_size else 0
