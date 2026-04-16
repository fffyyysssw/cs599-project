from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.attachment import Attachment
from app.models.user import User
from app.utils.helpers import build_upload_path


def save_upload(
    db: Session,
    current_user: User,
    upload_file: UploadFile,
    material_type: str | None = None,
) -> Attachment:
    settings = get_settings()
    file_name = upload_file.filename or "unnamed"
    content = upload_file.file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传文件不能为空")
    if len(content) > settings.max_upload_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传文件不能超过10MB")

    absolute_path, relative_path = build_upload_path(file_name, settings.upload_dir)
    Path(absolute_path).write_bytes(content)

    attachment = Attachment(
        application_id=None,
        file_name=file_name,
        file_path=relative_path,
        file_size=len(content),
        file_type=upload_file.content_type or "application/octet-stream",
        material_type=material_type or "other",
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment
