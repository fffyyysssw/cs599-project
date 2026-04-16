from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.application import Application
from app.models.approval_step import ApprovalStep
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.process_type import ProcessType
from app.models.user import User
from app.schemas.application import ApplicationCreate
from app.utils.helpers import (
    determine_approval_route,
    determine_required_materials,
    generate_application_no,
    normalize_form_data,
    resolve_approver,
    user_can_view_application,
    validate_required_fields,
    validate_required_materials,
)


def get_process_type_or_404(db: Session, code: str) -> ProcessType:
    process = db.scalar(select(ProcessType).where(ProcessType.code == code, ProcessType.is_active.is_(True)))
    if process is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="流程类型不存在")
    return process


def serialize_application_item(application: Application, include_applicant: bool = False) -> dict[str, Any]:
    data = {
        "id": application.id,
        "application_no": application.application_no,
        "title": application.title,
        "process_type": application.process_type,
        "status": application.status,
        "current_step": application.current_step,
        "total_steps": application.total_steps,
        "created_at": application.created_at,
    }
    if include_applicant:
        data["applicant"] = {
            "id": application.applicant.id,
            "real_name": application.applicant.real_name,
            "department": application.applicant.department,
        }
    return data


def serialize_application_detail(application: Application) -> dict[str, Any]:
    return {
        "id": application.id,
        "application_no": application.application_no,
        "title": application.title,
        "process_type": application.process_type,
        "applicant": {
            "id": application.applicant.id,
            "real_name": application.applicant.real_name,
            "department": application.applicant.department,
        },
        "status": application.status,
        "form_data": application.form_data,
        "ai_analysis": application.ai_analysis,
        "current_step": application.current_step,
        "total_steps": application.total_steps,
        "approval_steps": [
            {
                "id": step.id,
                "step_order": step.step_order,
                "approver_role": step.approver_role,
                "approver": (
                    {"id": step.approver.id, "real_name": step.approver.real_name} if step.approver else None
                ),
                "status": step.status,
                "comment": step.comment,
                "operated_at": step.operated_at,
                "created_at": step.created_at,
            }
            for step in application.approval_steps
        ],
        "attachments": [
            {
                "id": attachment.id,
                "file_name": attachment.file_name,
                "file_path": attachment.file_path,
                "file_size": attachment.file_size,
                "file_type": attachment.file_type,
                "material_type": attachment.material_type,
            }
            for attachment in application.attachments
        ],
        "audit_logs": [
            {
                "action": log.action,
                "operator": {"real_name": log.operator.real_name},
                "detail": log.detail,
                "created_at": log.created_at,
            }
            for log in sorted(application.audit_logs, key=lambda item: item.created_at)
        ],
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }


def create_application(
    db: Session,
    applicant: User,
    payload: ApplicationCreate,
    ip_address: str | None = None,
) -> Application:
    process = get_process_type_or_404(db, payload.process_type)
    normalized_form_data = normalize_form_data(payload.process_type, payload.form_data)
    validate_required_fields(payload.process_type, normalized_form_data)
    required_materials = determine_required_materials(payload.process_type, normalized_form_data)

    attachments: list[Attachment] = []
    if payload.attachment_ids:
        attachments = list(
            db.scalars(
                select(Attachment).where(
                    Attachment.id.in_(payload.attachment_ids),
                    Attachment.uploaded_by == applicant.id,
                )
            )
        )
        if len(attachments) != len(set(payload.attachment_ids)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="存在无效的附件记录")

    validate_required_materials(
        [attachment.material_type or "other" for attachment in attachments],
        required_materials,
    )

    route = determine_approval_route(payload.process_type, normalized_form_data)
    application = Application(
        application_no=generate_application_no(db, payload.process_type),
        title=payload.title,
        process_type=process.code,
        applicant_id=applicant.id,
        status="pending",
        form_data=normalized_form_data,
        ai_analysis=payload.ai_analysis,
        current_step=1,
        total_steps=len(route),
        remark=payload.remark,
    )
    db.add(application)
    db.flush()

    for index, role in enumerate(route, start=1):
        approver = resolve_approver(db, role, applicant)
        step = ApprovalStep(
            application_id=application.id,
            step_order=index,
            approver_role=role,
            approver_id=approver.id if approver else None,
            status="pending" if index == 1 else "waiting",
        )
        db.add(step)

    for attachment in attachments:
        attachment.application_id = application.id
        db.add(
            AuditLog(
                application_id=application.id,
                operator_id=applicant.id,
                action="upload",
                detail=f"关联附件：{attachment.file_name}",
                ip_address=ip_address,
            )
        )

    db.add(
        AuditLog(
            application_id=application.id,
            operator_id=applicant.id,
            action="submit",
            detail="提交申请",
            ip_address=ip_address,
        )
    )
    db.commit()
    return get_application_detail_entity(db, applicant, application.id)


def get_application_detail_entity(db: Session, current_user: User, application_id: int) -> Application:
    application = db.scalar(
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.applicant),
            selectinload(Application.approval_steps).selectinload(ApprovalStep.approver),
            selectinload(Application.attachments),
            selectinload(Application.audit_logs).selectinload(AuditLog.operator),
        )
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申请不存在")
    if not user_can_view_application(current_user, application):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该申请")
    return application


def get_my_applications(
    db: Session,
    current_user: User,
    page: int,
    page_size: int,
    status_filter: str | None = None,
    process_type: str | None = None,
) -> dict[str, Any]:
    conditions = [Application.applicant_id == current_user.id]
    if status_filter:
        conditions.append(Application.status == status_filter)
    if process_type:
        conditions.append(Application.process_type == process_type)

    total = db.scalar(select(func.count(Application.id)).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Application)
            .where(*conditions)
            .order_by(Application.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [serialize_application_item(item) for item in items],
    }
