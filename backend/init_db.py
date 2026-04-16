from pathlib import Path

from app.core.config import get_settings
from app.db.base import Base
from app.db.database import engine
from app.models import application, approval_step, attachment, audit_log, process_type, user  # noqa: F401


def main() -> None:
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成。")


if __name__ == "__main__":
    main()
