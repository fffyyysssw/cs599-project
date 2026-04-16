from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.schemas.common import success_response
from app.services.upload_service import save_upload


router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    material_type: str | None = Form(default="other"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    attachment = save_upload(db, current_user, file, material_type)
    return success_response(
        {
            "id": attachment.id,
            "file_name": attachment.file_name,
            "file_path": attachment.file_path,
            "file_size": attachment.file_size,
            "file_type": attachment.file_type,
            "material_type": attachment.material_type,
        },
        message="上传成功",
    )
