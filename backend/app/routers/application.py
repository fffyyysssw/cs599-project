from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.schemas.application import ApplicationCreate
from app.schemas.common import success_response
from app.services.application_service import (
    create_application,
    get_application_detail_entity,
    get_my_applications,
    serialize_application_detail,
)


router = APIRouter(prefix="/applications", tags=["申请"])


@router.post("")
async def create_new_application(
    payload: ApplicationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    application = create_application(
        db,
        current_user,
        payload,
        ip_address=request.client.host if request.client else None,
    )
    return success_response(serialize_application_detail(application), message="申请提交成功")


@router.get("/my")
async def list_my_applications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    status: str | None = Query(default=None),
    process_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data = get_my_applications(db, current_user, page, page_size, status, process_type)
    return success_response(data, message="获取成功")


@router.get("/{application_id}")
async def get_application_detail(
    application_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    application = get_application_detail_entity(db, current_user, application_id)
    return success_response(serialize_application_detail(application), message="获取成功")
