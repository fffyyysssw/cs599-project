from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.schemas.approval import ApprovalAction
from app.schemas.common import success_response
from app.services.approval_service import get_pending_approvals, handle_approval_action


router = APIRouter(prefix="/approvals", tags=["审批"])


@router.get("/pending")
async def list_pending_approvals(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    process_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data = get_pending_approvals(db, current_user, page, page_size, process_type)
    return success_response(data, message="获取成功")


@router.post("/{step_id}/approve")
async def approve(
    step_id: int,
    payload: ApprovalAction,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data = handle_approval_action(
        db,
        current_user,
        step_id,
        "approve",
        payload.comment,
        ip_address=request.client.host if request.client else None,
    )
    return success_response(data, message="审批通过成功")


@router.post("/{step_id}/reject")
async def reject(
    step_id: int,
    payload: ApprovalAction,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data = handle_approval_action(
        db,
        current_user,
        step_id,
        "reject",
        payload.comment,
        ip_address=request.client.host if request.client else None,
    )
    return success_response(data, message="审批驳回成功")


@router.post("/{step_id}/return")
async def return_application(
    step_id: int,
    payload: ApprovalAction,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data = handle_approval_action(
        db,
        current_user,
        step_id,
        "return",
        payload.comment,
        ip_address=request.client.host if request.client else None,
    )
    return success_response(data, message="审批退回成功")
