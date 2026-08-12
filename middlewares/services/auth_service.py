import datetime
from repositories.user_repository import UserRepository
from schemas import UserRegisterRequest, UserLoginRequest
import jwt
import bcrypt
from utils.errorHandler.error_handler import AppError
from core.config import settings


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login_user(self, user_body: UserLoginRequest):
        user = await self.user_repository.find_by_email(user_body.email)
        if not user:
            raise AppError("Invalid email or password", 404, "INVALID_CREDITENTIALS")
        print("useruseruseruser", user["hashed_password"])
        is_matched = bcrypt.checkpw(
            user_body.password.encode("utf-8"),  # Convert plain password to bytes
            user["hashed_password"].encode("utf-8"),
        )

        if not is_matched:
            raise AppError("Invalid creditentials", 404, "INVALID_CREDITENTIALS")

        jwt_token = jwt.encode(
            {
                "user_id": str(user["_id"]),
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=7),
            },
            key=settings.JWT_SECRET,
            algorithm="HS256",
        )
        return jwt_token

    async def register_user(self, new_user: UserRegisterRequest):
        existing_user = await self.user_repository.find_by_email(new_user.email)

        if existing_user:
            raise AppError(
                "User already exists",
                409,
                "USER_EXISTS",
            )

        salt = bcrypt.gensalt()

        hashed_password = bcrypt.hashpw(
            new_user.password.encode("utf-8"),
            salt,
        ).decode("utf-8")

        user_data = {
            "username": new_user.username,
            "email": new_user.email,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_superuser": False,
        }

        created_user = await self.user_repository.create(user_data)

        if not created_user:
            raise AppError(
                "Failed to create user",
                500,
                "USER_CREATION_FAILED",
            )

        token = jwt.encode(
            {
                "user_id": str(created_user.inserted_id),
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=7),
            },
            settings.JWT_SECRET,
            algorithm="HS256",
        )

        return token
