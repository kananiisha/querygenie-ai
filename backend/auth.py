"""
JWT Authentication utilities.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Render sets RENDER=true; you can also set ENV=production on any other host.
IS_PRODUCTION = bool(os.environ.get("RENDER")) or os.environ.get("ENV", "").lower() == "production"

# Placeholder values that must never be used to sign real tokens.
_WEAK_KEYS = {"", "change_me", "changeme", "querygenie-dev-secret-key-change-me"}


def _load_secret_key() -> str:
    key = os.environ.get("SECRET_KEY", "").strip()
    if key and key not in _WEAK_KEYS:
        return key
    if IS_PRODUCTION:
        raise RuntimeError(
            "SECRET_KEY is missing or a placeholder. Set it to a long random value "
            "(for example: python -c \"import secrets; print(secrets.token_urlsafe(32))\")."
        )
    # Local development only: random per-process key, so there is no guessable default.
    # Tokens stop working when the server restarts.
    return secrets.token_urlsafe(32)


SECRET_KEY = _load_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# True (default): requests without a token run as a shared demo user, so the public
# demo works without sign-up. Set ALLOW_ANONYMOUS=false to require a valid token.
ALLOW_ANONYMOUS = os.environ.get("ALLOW_ANONYMOUS", "true").strip().lower() == "true"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str | None = Depends(oauth2_scheme)) -> dict:
    if not token:
        if ALLOW_ANONYMOUS:
            return {"sub": "demo-user", "email": "demo@localhost"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )