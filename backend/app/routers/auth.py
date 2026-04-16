from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest
from app.schemas.common import success_response
from app.services.auth_service import authenticate_user, build_user_info


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = create_access_token(
        {"sub": user.username, "role": user.role, "user_id": user.id}
    )
    return success_response(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": build_user_info(user),
        },
        message="登录成功",
    )


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return success_response(build_user_info(current_user), message="获取成功")
