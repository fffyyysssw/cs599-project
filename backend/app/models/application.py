from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.approval_step import ApprovalStep
    from app.models.attachment import Attachment
    from app.models.audit_log import AuditLog
    from app.models.process_type import ProcessType
    from app.models.user import User


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    application_no: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    process_type: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("process_types.code"),
        nullable=False,
        index=True,
    )
    applicant_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    form_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    ai_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    current_step: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    applicant: Mapped["User"] = relationship(back_populates="applications")
    process: Mapped["ProcessType"] = relationship(back_populates="applications")
    approval_steps: Mapped[list["ApprovalStep"]] = relationship(
        back_populates="application",
        order_by="ApprovalStep.step_order",
        cascade="all, delete-orphan",
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
    )
