from services.auth_service import AuthService
from dependencies.repositories import fetch_user_repository
from repositories.user_repository import UserRepository
from fastapi import Depends
from repositories.session_repository import SessionRepository


def get_auth_service(repo: UserRepository = Depends(fetch_user_repository)):
    return AuthService(repo)


def get_session_repository():
    return SessionRepository()
