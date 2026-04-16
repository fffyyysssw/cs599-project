from pydantic import BaseModel, Field, field_validator


class ApprovalAction(BaseModel):
    comment: str = Field(min_length=1, max_length=500)

    @field_validator("comment")
    @classmethod
    def strip_comment(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("审批意见不能为空")
        return value
