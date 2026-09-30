import datetime
from repositories.user_repository import UserRepository
from schemas import UserRegisterRequest, UserLoginRequest
import jwt
import bcrypt
from utils.errorHandler.error_handler import AppError
from core.config import settings


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def switch_admin(self, user_id: str, turn_admin: bool):
        user_repository = self.user_repository
        user =  await user_repository.update(user_id=user_id, data={"is_admin": turn_admin})
        print("user------------")
        print(user)
