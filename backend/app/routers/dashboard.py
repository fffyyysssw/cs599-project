from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.application import Application
from app.models.approval_step import ApprovalStep
from app.schemas.common import success_response
from app.services.application_service import serialize_application_item


router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    my_pending = db.scalar(
        select(func.count(Application.id)).where(
            Application.applicant_id == current_user.id,
            Application.status == "pending",
        )
    ) or 0
    my_approved = db.scalar(
        select(func.count(Application.id)).where(
            Application.applicant_id == current_user.id,
            Application.status == "approved",
        )
    ) or 0
    my_rejected = db.scalar(
        select(func.count(Application.id)).where(
            Application.applicant_id == current_user.id,
            Application.status == "rejected",
        )
    ) or 0

    approval_conditions = [ApprovalStep.status == "pending"]
    if current_user.role != "admin":
        approval_conditions.append(
            or_(
                ApprovalStep.approver_id == current_user.id,
                ApprovalStep.approver_id.is_(None),
                ApprovalStep.approver_role == current_user.role,
            )
        )
    need_my_approval = db.scalar(select(func.count(ApprovalStep.id)).where(*approval_conditions)) or 0

    recent_applications = list(
        db.scalars(
            select(Application)
            .where(Application.applicant_id == current_user.id)
            .order_by(Application.created_at.desc())
            .limit(5)
        )
    )

    return success_response(
        {
            "my_pending": my_pending,
            "my_approved": my_approved,
            "my_rejected": my_rejected,
            "need_my_approval": need_my_approval,
            "recent_applications": [serialize_application_item(item) for item in recent_applications],
        },
        message="获取成功",
    )
