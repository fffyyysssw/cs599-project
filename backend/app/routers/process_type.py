from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.deps import get_db
from app.models.process_type import ProcessType
from app.schemas.common import success_response


router = APIRouter(prefix="/process-types", tags=["流程类型"])


@router.get("")
async def list_process_types(db: Session = Depends(get_db)):
    items = list(
        db.scalars(
            select(ProcessType)
            .where(ProcessType.is_active.is_(True))
            .order_by(ProcessType.id.asc())
        )
    )
    data = [
        {
            "id": item.id,
            "code": item.code,
            "name": item.name,
            "description": item.description,
            "form_schema": item.form_schema,
            "rules": item.rules,
        }
        for item in items
    ]
    return success_response(data, message="获取成功")


@router.get("/{code}")
async def get_process_type(code: str, db: Session = Depends(get_db)):
    item = db.scalar(select(ProcessType).where(ProcessType.code == code, ProcessType.is_active.is_(True)))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="流程类型不存在")
    return success_response(
        {
            "id": item.id,
            "code": item.code,
            "name": item.name,
            "description": item.description,
            "form_schema": item.form_schema,
            "rules": item.rules,
        },
        message="获取成功",
    )
