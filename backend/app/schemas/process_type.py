from typing import Any

from pydantic import BaseModel, ConfigDict


class ProcessTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    form_schema: dict[str, Any]
    rules: dict[str, Any]
