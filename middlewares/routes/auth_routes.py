from fastapi.routing import APIRouter
from schemas import UserRegisterRequest, UserLoginRequest
from fastapi import Depends
from dependencies.services import get_auth_service
from services.auth_service import AuthService

auth_router = APIRouter()


@auth_router.post("/register")
async def register(
    body: UserRegisterRequest, service: AuthService = Depends(get_auth_service)
):
    jwt_token = await service.register_user(body)

    return {
        "success": True,
        "message": "User registered successfully",
        "data": body,
        "token": jwt_token,
    }


@auth_router.post("/login")
async def register(
    body: UserLoginRequest, service: AuthService = Depends(get_auth_service)
):
    jwt_token = await service.login_user(body)

    return {
        "success": True,
        "message": "User Loggedin successfully",
        "data": body,
        "token": jwt_token,
    }
