from datetime import datetime

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.models.application import Application
from app.models.approval_step import ApprovalStep
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.process_type import ProcessType
from app.models.user import User
from app.utils.helpers import get_process_templates


USERS = [
    {"username": "zhangsan", "password": "123456", "role": "employee", "department": "技术部", "real_name": "张三"},
    {"username": "lisi", "password": "123456", "role": "manager", "department": "技术部", "real_name": "李四"},
    {"username": "wangwu", "password": "123456", "role": "finance", "department": "财务部", "real_name": "王五"},
    {"username": "zhaoliu", "password": "123456", "role": "hr", "department": "人力资源部", "real_name": "赵六"},
    {"username": "sunqi", "password": "123456", "role": "procurement", "department": "采购部", "real_name": "孙七"},
    {"username": "admin", "password": "123456", "role": "admin", "department": "管理层", "real_name": "管理员"},
]


def ensure_users(db):
    for item in USERS:
        user = db.scalar(select(User).where(User.username == item["username"]))
        if user is None:
            user = User(
                username=item["username"],
                password_hash=get_password_hash(item["password"]),
                role=item["role"],
                department=item["department"],
                real_name=item["real_name"],
                is_active=True,
            )
            db.add(user)
        else:
            user.password_hash = get_password_hash(item["password"])
            user.role = item["role"]
            user.department = item["department"]
            user.real_name = item["real_name"]
            user.is_active = True
    db.flush()


def ensure_process_types(db):
    for item in get_process_templates():
        process = db.scalar(select(ProcessType).where(ProcessType.code == item["code"]))
        if process is None:
            process = ProcessType(**item)
            db.add(process)
        else:
            process.name = item["name"]
            process.description = item["description"]
            process.form_schema = item["form_schema"]
            process.rules = item["rules"]
            process.is_active = True
    db.flush()


def user_map(db):
    return {user.username: user for user in db.scalars(select(User)).all()}


def ensure_application(db, application_no, **kwargs):
    existing = db.scalar(select(Application).where(Application.application_no == application_no))
    if existing is not None:
        return existing

    application = Application(application_no=application_no, **kwargs)
    db.add(application)
    db.flush()
    return application


def ensure_step(db, application_id, step_order, **kwargs):
    step = db.scalar(
        select(ApprovalStep).where(
            ApprovalStep.application_id == application_id,
            ApprovalStep.step_order == step_order,
        )
    )
    if step is None:
        step = ApprovalStep(application_id=application_id, step_order=step_order, **kwargs)
        db.add(step)
        db.flush()
    return step


def ensure_attachment(db, application_id, file_name, **kwargs):
    attachment = db.scalar(
        select(Attachment).where(
            Attachment.application_id == application_id,
            Attachment.file_name == file_name,
        )
    )
    if attachment is None:
        attachment = Attachment(application_id=application_id, file_name=file_name, **kwargs)
        db.add(attachment)
        db.flush()
    return attachment


def ensure_log(db, application_id, action, detail, operator_id, step_id=None):
    log = db.scalar(
        select(AuditLog).where(
            AuditLog.application_id == application_id,
            AuditLog.action == action,
            AuditLog.detail == detail,
        )
    )
    if log is None:
        log = AuditLog(
            application_id=application_id,
            step_id=step_id,
            operator_id=operator_id,
            action=action,
            detail=detail,
        )
        db.add(log)
        db.flush()
    return log


def seed_applications(db):
    users = user_map(db)
    created_at = datetime(2026, 3, 25, 9, 0, 0)

    app1 = ensure_application(
        db,
        "LV20260325001",
        title="事假申请-3天",
        process_type="leave",
        applicant_id=users["zhangsan"].id,
        status="pending",
        form_data={
            "leave_type": "事假",
            "start_date": "2026-04-13",
            "end_date": "2026-04-15",
            "days": 3,
            "reason": "家里有事",
            "handover_person": "王小明",
        },
        ai_analysis={
            "process_type": "leave",
            "confidence": 0.95,
            "title": "事假申请-3天",
            "extracted_fields": {
                "leave_type": "事假",
                "start_date": "2026-04-13",
                "end_date": "2026-04-15",
                "days": 3,
                "reason": "家里有事",
            },
            "missing_fields": ["handover_person"],
            "required_materials": [],
            "approval_route": ["manager", "hr"],
            "risk_tips": [],
            "summary": "申请人提交3天事假申请，仍需补充工作交接人信息。",
        },
        current_step=1,
        total_steps=2,
        remark="课程演示数据",
        created_at=created_at,
        updated_at=created_at,
    )
    step1 = ensure_step(
        db,
        app1.id,
        1,
        approver_role="manager",
        approver_id=users["lisi"].id,
        status="pending",
    )
    ensure_step(
        db,
        app1.id,
        2,
        approver_role="hr",
        approver_id=users["zhaoliu"].id,
        status="waiting",
    )
    ensure_log(db, app1.id, "submit", "提交申请", users["zhangsan"].id)

    app2 = ensure_application(
        db,
        "RB20260325001",
        title="差旅报销-800元",
        process_type="reimbursement",
        applicant_id=users["zhangsan"].id,
        status="approved",
        form_data={
            "reimbursement_type": "差旅",
            "amount": 800,
            "expense_date": "2026-03-20",
            "reason": "客户拜访交通费用",
            "invoice_no": "INV20260320001",
        },
        ai_analysis={
            "process_type": "reimbursement",
            "confidence": 0.93,
            "title": "差旅报销-800元",
            "extracted_fields": {
                "reimbursement_type": "差旅",
                "amount": 800,
                "expense_date": "2026-03-20",
                "reason": "客户拜访交通费用",
                "invoice_no": "INV20260320001",
            },
            "missing_fields": [],
            "required_materials": ["invoice"],
            "approval_route": ["manager"],
            "risk_tips": ["报销必须上传发票"],
            "summary": "申请人提交差旅报销800元，主管已审批通过。",
        },
        current_step=1,
        total_steps=1,
        remark="课程演示数据",
        created_at=created_at,
        updated_at=created_at,
    )
    step2 = ensure_step(
        db,
        app2.id,
        1,
        approver_role="manager",
        approver_id=users["lisi"].id,
        status="approved",
        comment="同意报销",
        operated_at=datetime(2026, 3, 25, 10, 0, 0),
    )
    ensure_attachment(
        db,
        app2.id,
        "发票_差旅.pdf",
        file_path="uploads/2026-03-25/invoice_demo.pdf",
        file_size=102400,
        file_type="application/pdf",
        material_type="invoice",
        uploaded_by=users["zhangsan"].id,
    )
    ensure_log(db, app2.id, "submit", "提交申请", users["zhangsan"].id)
    ensure_log(db, app2.id, "approve", "同意报销", users["lisi"].id, step_id=step2.id)

    app3 = ensure_application(
        db,
        "PC20260325001",
        title="采购申请-键盘20件",
        process_type="purchase",
        applicant_id=users["zhangsan"].id,
        status="rejected",
        form_data={
            "item_name": "键盘",
            "quantity": 20,
            "unit_price": 225,
            "total_amount": 4500,
            "purpose": "项目组设备更新",
            "supplier": "罗技",
        },
        ai_analysis={
            "process_type": "purchase",
            "confidence": 0.97,
            "title": "采购申请-键盘20台",
            "extracted_fields": {
                "item_name": "键盘",
                "quantity": 20,
                "unit_price": 225,
                "total_amount": 4500,
                "purpose": "项目组设备更新",
                "supplier": "罗技",
            },
            "missing_fields": [],
            "required_materials": ["quotation"],
            "approval_route": ["manager", "procurement"],
            "risk_tips": ["采购金额超过3000元，需要上传报价单"],
            "summary": "采购申请金额4500元，采购已驳回。",
        },
        current_step=2,
        total_steps=2,
        remark="课程演示数据",
        created_at=created_at,
        updated_at=created_at,
    )
    step3_1 = ensure_step(
        db,
        app3.id,
        1,
        approver_role="manager",
        approver_id=users["lisi"].id,
        status="approved",
        comment="同意进入采购审批",
        operated_at=datetime(2026, 3, 25, 10, 30, 0),
    )
    step3_2 = ensure_step(
        db,
        app3.id,
        2,
        approver_role="procurement",
        approver_id=users["sunqi"].id,
        status="rejected",
        comment="供应商报价偏高，请重新询价",
        operated_at=datetime(2026, 3, 25, 11, 0, 0),
    )
    ensure_attachment(
        db,
        app3.id,
        "报价单_键盘.pdf",
        file_path="uploads/2026-03-25/quotation_demo.pdf",
        file_size=204800,
        file_type="application/pdf",
        material_type="quotation",
        uploaded_by=users["zhangsan"].id,
    )
    ensure_log(db, app3.id, "submit", "提交申请", users["zhangsan"].id)
    ensure_log(db, app3.id, "approve", "同意进入采购审批", users["lisi"].id, step_id=step3_1.id)
    ensure_log(db, app3.id, "reject", "供应商报价偏高，请重新询价", users["sunqi"].id, step_id=step3_2.id)

    app4 = ensure_application(
        db,
        "RB20260325002",
        title="差旅报销-6000元",
        process_type="reimbursement",
        applicant_id=users["lisi"].id,
        status="pending",
        form_data={
            "reimbursement_type": "差旅",
            "amount": 6000,
            "expense_date": "2026-03-18",
            "reason": "出差住宿费",
            "invoice_no": "INV20260318001",
        },
        ai_analysis={
            "process_type": "reimbursement",
            "confidence": 0.92,
            "title": "差旅报销-6000元",
            "extracted_fields": {
                "reimbursement_type": "差旅",
                "amount": 6000,
                "expense_date": "2026-03-18",
                "reason": "出差住宿费",
                "invoice_no": "INV20260318001",
            },
            "missing_fields": [],
            "required_materials": ["invoice"],
            "approval_route": ["manager", "department_head", "finance"],
            "risk_tips": ["报销金额超过5000元，需要部门负责人额外审批"],
            "summary": "申请人提交差旅报销6000元，当前待财务审批。",
        },
        current_step=3,
        total_steps=3,
        remark="课程演示数据",
        created_at=created_at,
        updated_at=created_at,
    )
    step4_1 = ensure_step(
        db,
        app4.id,
        1,
        approver_role="manager",
        approver_id=users["admin"].id,
        status="approved",
        comment="已审阅",
        operated_at=datetime(2026, 3, 25, 9, 30, 0),
    )
    step4_2 = ensure_step(
        db,
        app4.id,
        2,
        approver_role="department_head",
        approver_id=users["admin"].id,
        status="approved",
        comment="同意报销",
        operated_at=datetime(2026, 3, 25, 9, 45, 0),
    )
    ensure_step(
        db,
        app4.id,
        3,
        approver_role="finance",
        approver_id=users["wangwu"].id,
        status="pending",
    )
    ensure_attachment(
        db,
        app4.id,
        "发票_住宿.pdf",
        file_path="uploads/2026-03-25/invoice_hotel_demo.pdf",
        file_size=307200,
        file_type="application/pdf",
        material_type="invoice",
        uploaded_by=users["lisi"].id,
    )
    ensure_log(db, app4.id, "submit", "提交申请", users["lisi"].id)
    ensure_log(db, app4.id, "approve", "已审阅", users["admin"].id, step_id=step4_1.id)
    ensure_log(db, app4.id, "approve", "同意报销", users["admin"].id, step_id=step4_2.id)

    app5 = ensure_application(
        db,
        "LV20260325002",
        title="病假申请-4天",
        process_type="leave",
        applicant_id=users["sunqi"].id,
        status="returned",
        form_data={
            "leave_type": "病假",
            "start_date": "2026-03-26",
            "end_date": "2026-03-29",
            "days": 4,
            "reason": "身体不适",
            "handover_person": "周同学",
        },
        ai_analysis={
            "process_type": "leave",
            "confidence": 0.94,
            "title": "病假申请-4天",
            "extracted_fields": {
                "leave_type": "病假",
                "start_date": "2026-03-26",
                "end_date": "2026-03-29",
                "days": 4,
                "reason": "身体不适",
                "handover_person": "周同学",
            },
            "missing_fields": [],
            "required_materials": ["sick_leave_certificate"],
            "approval_route": ["manager", "department_head", "hr"],
            "risk_tips": ["病假超过2天，请上传病假证明"],
            "summary": "病假申请已被退回，申请人需补充材料后重新提交。",
        },
        current_step=1,
        total_steps=3,
        remark="课程演示数据",
        created_at=created_at,
        updated_at=created_at,
    )
    step5 = ensure_step(
        db,
        app5.id,
        1,
        approver_role="manager",
        approver_id=users["admin"].id,
        status="returned",
        comment="请补充更完整的病假证明",
        operated_at=datetime(2026, 3, 25, 11, 30, 0),
    )
    ensure_step(
        db,
        app5.id,
        2,
        approver_role="department_head",
        approver_id=users["admin"].id,
        status="waiting",
    )
    ensure_step(
        db,
        app5.id,
        3,
        approver_role="hr",
        approver_id=users["zhaoliu"].id,
        status="waiting",
    )
    ensure_attachment(
        db,
        app5.id,
        "病假证明.pdf",
        file_path="uploads/2026-03-25/sick_leave_demo.pdf",
        file_size=256000,
        file_type="application/pdf",
        material_type="sick_leave_certificate",
        uploaded_by=users["sunqi"].id,
    )
    ensure_log(db, app5.id, "submit", "提交申请", users["sunqi"].id)
    ensure_log(db, app5.id, "return", "请补充更完整的病假证明", users["admin"].id, step_id=step5.id)


def main():
    with SessionLocal() as db:
        ensure_users(db)
        ensure_process_types(db)
        seed_applications(db)
        db.commit()
        print("测试数据写入完成。")


if __name__ == "__main__":
    main()
