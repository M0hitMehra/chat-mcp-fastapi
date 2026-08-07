import jwt

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings
from utils.errorHandler.error_handler import AppError

security = HTTPBearer()


def authenticate_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET,
            algorithms=["HS256"],
        )

        user_id = payload.get("user_id")

        if not user_id:
            raise AppError(
                "Invalid token",
                401,
                "INVALID_TOKEN",
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise AppError(
            "Token has expired",
            401,
            "TOKEN_EXPIRED",
        )

    except jwt.InvalidTokenError:
        raise AppError(
            "Invalid token",
            401,
            "INVALID_TOKEN",
        )
