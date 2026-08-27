from datetime import timedelta

from jose import JWTError, jwt

from app.core.config import settings
from app.core.time import utc_now


def create_access_token(data: dict):

    payload = data.copy()

    expire = utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload["exp"] = expire

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str):

    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
