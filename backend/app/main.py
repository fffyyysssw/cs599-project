from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.routers import ai, application, approval, auth, dashboard, process_type, upload
from app.schemas.common import error_response, success_response


settings = get_settings()
app = FastAPI(title="SmartFlow API", version="1.0.0")

upload_dir = Path(settings.upload_dir)
upload_dir.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

app.include_router(auth.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(process_type.router, prefix="/api")
app.include_router(application.router, prefix="/api")
app.include_router(approval.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
async def root():
    return success_response({"name": "SmartFlow API", "version": "1.0.0"}, message="服务运行中")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return error_response(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    message = "；".join(error.get("msg", "数据校验失败") for error in exc.errors())
    return error_response(message or "数据校验失败", status_code=422)


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    message = str(exc) if settings.debug else "服务器内部错误"
    return error_response(message, status_code=500)
