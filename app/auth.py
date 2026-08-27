from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Header
from passlib.context import CryptContext

from app.errors import AppError

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

_USERS = {
    "admin": _pwd_context.hash(os.environ.get("DEMO_USER_PASSWORD", "admin123")),
}


def authenticate_user(username: str, password: str) -> bool:
    hashed = _USERS.get(username)
    if hashed is None:
        return False
    return _pwd_context.verify(password, hashed)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(authorization: Optional[str] = Header(default=None)) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise AppError(401, "UNAUTHORIZED", "missing bearer token")

    token = authorization[len("Bearer ") :]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AppError(401, "UNAUTHORIZED", "token has expired")
    except jwt.InvalidTokenError:
        raise AppError(401, "UNAUTHORIZED", "invalid token")

    username = payload.get("sub")
    if username is None or username not in _USERS:
        raise AppError(401, "UNAUTHORIZED", "invalid token subject")
    return username
