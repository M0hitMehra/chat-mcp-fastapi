from fastapi.routing import APIRouter
from fastapi import Depends

# dependecies
from dependencies.repositories import (
    fetch_user_repository,
    fetch_thread_repository,
    fetch_message_repository,
)
from dependencies.services import fetch_user_repository, fetch_user_service

from utils.errorHandler.error_handler import AppError
from middlewares.authenticate_user import is_user_admin, is_user_superadmin

# repos
from repositories.thread_repositories import ThreadRepository
from repositories.message_repository import MessageRepository
from repositories.user_repository import UserRepository

# services
from services.user_service import UserService

admin_router = APIRouter()


@admin_router.post("/users")
async def get_all_users(
    user_repository: UserRepository = Depends(fetch_user_repository),
    _: None = Depends(is_user_admin),
):
    users = await user_repository.find_all_users()
    return users


@admin_router.get("/user/threads/{user_id}")
async def get_threads(
    user_id: str,
    thread_repository: ThreadRepository = Depends(fetch_thread_repository),
    _: None = Depends(is_user_admin),
):
    threads = await thread_repository.find_by_user_id(user_id)

    return {
        "success": True,
        "threads": [
            {
                "id": str(thread["_id"]),
                "thread_id": thread["thread_id"],
                "thread_name": thread["thread_name"],
                "created_at": thread.get("created_at"),
                "updated_at": thread.get("updated_at"),
            }
            for thread in threads
        ],
    }


@admin_router.get("/user/messages")
async def get_thread_messages(
    thread_id: str,
    user_id: str,
    limit: int = 100,
    skip: int = 0,
    thread_repository: ThreadRepository = Depends(fetch_thread_repository),
    message_repository: MessageRepository = Depends(fetch_message_repository),
):

    if thread_id is None or user_id is None:
        raise AppError(
            message="Either thread id or user id is missing",
            status_code=404,
            error_code="MISSING_PAYLOAD",
        )

    thread = await thread_repository.find_by_user_id_and_thread_id(
        user_id=user_id,
        thread_id=thread_id,
    )

    if not thread:
        raise AppError(
            "Thread not found",
            404,
            "THREAD_NOT_FOUND",
        )

    messages = await message_repository.find_by_thread_id(
        thread_id=thread_id, user_id=user_id, skip=skip, limit=limit
    )

    return {
        "success": True,
        "messages": [
            {
                "id": str(message["_id"]),
                "role": message["role"],
                "content": message["content"],
                "created_at": message["created_at"],
            }
            for message in messages
        ],
    }


@admin_router.get("/switch/user")
async def switch_admin(
    user_id: str,
    make_admin: bool,
    _: None = Depends(is_user_superadmin),
     user_service: UserService = Depends(fetch_user_service),
):

    await user_service.switch_admin(user_id=user_id, turn_admin=make_admin)
    return {
        "success": True,
        "message": (
            "User switched to " + "basic user" if make_admin == False else "admin"
        ),
        "data": None,
    }
