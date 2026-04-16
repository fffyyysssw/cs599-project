from typing import Any

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("输入内容不能为空")
        return value


class AnalyzeResponseData(BaseModel):
    process_type: str
    confidence: float
    title: str
    extracted_fields: dict[str, Any]
    missing_fields: list[str]
    required_materials: list[str]
    approval_route: list[str]
    risk_tips: list[str]
    summary: str
