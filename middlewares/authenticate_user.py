import jwt

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings
from utils.errorHandler.error_handler import AppError
from dependencies.repositories import fetch_user_repository
from repositories.user_repository import UserRepository

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


async def is_user_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepository = Depends(fetch_user_repository),
) -> bool:

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

        user = await user_repository.find_by_id(user_id=user_id)

        if user["is_superuser"] != True:
            if user.get("is_admin") != True or user["is_admin"] != True:
                print("UNAUTHORIZED_ACCESSUNAUTHORIZED_ACCESSUNAUTHORIZED_ACCESS")
                raise AppError(
                    message="User is not admin",
                    status_code=401,
                    error_code="UNAUTHORIZED_ACCESS",
                )
        return True

    except Exception as e:
        print("------")
        print(e)
        raise AppError(
            message="User is not admin",
            status_code=401,
            error_code="e",
        )


async def is_user_superadmin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepository = Depends(fetch_user_repository),
) -> bool:

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

        user = await user_repository.find_by_id(user_id=user_id)
        if user["is_superuser"] == True:
            return True
        raise AppError(
            message="User is not super user",
            status_code=401,
            error_code="UNAUTHORIZED_ACCESS",
        )

    except Exception as e:
        raise AppError(
            message="User is not super user",
            status_code=401,
            error_code=e,
        )
