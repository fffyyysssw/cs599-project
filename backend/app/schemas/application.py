from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


ALLOWED_PROCESS_TYPES = {"leave", "reimbursement", "purchase"}


class ApplicationCreate(BaseModel):
    process_type: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=200)
    form_data: dict[str, Any]
    ai_analysis: dict[str, Any] | None = None
    attachment_ids: list[int] = Field(default_factory=list)
    remark: str | None = Field(default=None, max_length=500)

    @field_validator("process_type", "title", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def validate_payload(self) -> "ApplicationCreate":
        if self.process_type not in ALLOWED_PROCESS_TYPES:
            raise ValueError("不支持的流程类型")
        if not self.form_data:
            raise ValueError("表单数据不能为空")
        if not self.title:
            raise ValueError("申请标题不能为空")
        return self
