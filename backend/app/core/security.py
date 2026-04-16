from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any

from jose import jwt

from app.core.config import get_settings


ALGORITHM = "HS256"
HASH_PREFIX = "sha256$"


def _sha256(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith(HASH_PREFIX):
        return _sha256(plain_password) == hashed_password.removeprefix(HASH_PREFIX)
    return _sha256(plain_password) == hashed_password


def get_password_hash(password: str) -> str:
    return f"{HASH_PREFIX}{_sha256(password)}"


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
