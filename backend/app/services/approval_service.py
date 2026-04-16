from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.application import Application
from app.models.approval_step import ApprovalStep
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.helpers import now_shanghai, user_can_approve_step
from app.services.application_service import serialize_application_item


def get_pending_approvals(
    db: Session,
    current_user: User,
    page: int,
    page_size: int,
    process_type: str | None = None,
) -> dict[str, Any]:
    conditions = [ApprovalStep.status == "pending"]
    if process_type:
        conditions.append(Application.process_type == process_type)

    if current_user.role != "admin":
        conditions.append(
            or_(
                ApprovalStep.approver_id == current_user.id,
                ApprovalStep.approver_id.is_(None),
                ApprovalStep.approver_role == current_user.role,
            )
        )

    total = db.scalar(
        select(func.count(ApprovalStep.id)).join(Application).where(*conditions)
    ) or 0

    steps = list(
        db.scalars(
            select(ApprovalStep)
            .join(Application)
            .where(*conditions)
            .options(selectinload(ApprovalStep.application).selectinload(Application.applicant))
            .order_by(Application.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            serialize_application_item(step.application, include_applicant=True)
            for step in steps
        ],
    }


def handle_approval_action(
    db: Session,
    current_user: User,
    step_id: int,
    action: str,
    comment: str,
    ip_address: str | None = None,
) -> dict[str, Any]:
    step = db.scalar(
        select(ApprovalStep)
        .where(ApprovalStep.id == step_id)
        .options(
            selectinload(ApprovalStep.application).selectinload(Application.approval_steps),
        )
    )
    if step is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批步骤不存在")
    if step.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前步骤不可操作")
    if not user_can_approve_step(current_user, step.approver_id, step.approver_role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权审批该步骤")

    application = step.application
    now = now_shanghai().replace(tzinfo=None)
    step.comment = comment
    step.operated_at = now

    if action == "approve":
        step.status = "approved"
        next_step = next(
            (item for item in sorted(application.approval_steps, key=lambda current: current.step_order) if item.step_order == step.step_order + 1),
            None,
        )
        if next_step is None:
            application.status = "approved"
        else:
            next_step.status = "pending"
            application.current_step = next_step.step_order
            application.status = "pending"
    elif action == "reject":
        step.status = "rejected"
        application.status = "rejected"
    elif action == "return":
        step.status = "returned"
        application.status = "returned"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的审批动作")

    db.add(
        AuditLog(
            application_id=application.id,
            step_id=step.id,
            operator_id=current_user.id,
            action=action,
            detail=comment,
            ip_address=ip_address,
        )
    )
    db.commit()
    return {
        "application_id": application.id,
        "status": application.status,
        "current_step": application.current_step,
        "total_steps": application.total_steps,
    }
