from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any | None = None


def success_response(data: Any = None, message: str = "操作成功", status_code: int = 200) -> JSONResponse:
    payload = ApiResponse(code=status_code, message=message, data=data)
    return JSONResponse(status_code=status_code, content=jsonable_encoder(payload.model_dump()))


def error_response(message: str, status_code: int = 400, data: Any = None) -> JSONResponse:
    payload = ApiResponse(code=status_code, message=message, data=data)
    return JSONResponse(status_code=status_code, content=jsonable_encoder(payload.model_dump()))
