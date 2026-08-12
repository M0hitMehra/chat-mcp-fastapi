from fastapi.routing import APIRouter

import datetime

from schemas import (
    CreateThreadRequest,
    UpdateThreadConfigRequest,
)
from utils.errorHandler.error_handler import AppError

from fastapi import Depends
from middlewares.authenticate_user import authenticate_user
from dependencies.repositories import fetch_session_repository
from repositories.session_repository import SessionRepository
from dependencies.repositories import fetch_thread_repository
from repositories.thread_repositories import ThreadRepository
from repositories.message_repository import MessageRepository
from dependencies.repositories import fetch_message_repository

import uuid

from bson import ObjectId

thread_router = APIRouter()


@thread_router.get("/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    user_id: str = Depends(authenticate_user),
    thread_repository: ThreadRepository = Depends(fetch_thread_repository),
    message_repository: MessageRepository = Depends(fetch_message_repository),
):
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
        thread_id=thread_id,
        user_id=user_id,
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


@thread_router.get("/")
async def get_threads(
    user_id: str = Depends(authenticate_user),
    thread_repository: ThreadRepository = Depends(fetch_thread_repository),
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


@thread_router.post("/")
async def create_thread(
    body: CreateThreadRequest,
    user_id: str = Depends(authenticate_user),
    session_repository: SessionRepository = Depends(fetch_session_repository),
    thread_repository: ThreadRepository = Depends(fetch_thread_repository),
):
    session = await session_repository.find_user_session(
        session_id=body.session_id,
        user_id=user_id,
    )

    if not session:
        raise AppError(
            "Session not found",
            404,
            "SESSION_NOT_FOUND",
        )

    thread_id = str(uuid.uuid4())

    await thread_repository.create(
        {
            "thread_id": thread_id,
            "thread_name": "New Chat",
            "session_id": body.session_id,
            "user_id": ObjectId(user_id),
            "model_name": body.model_name,
            "api_key": body.apiKey,
            "mcp_servers": [server.model_dump() for server in body.mcp_servers],
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        }
    )

    return {
        "thread_id": thread_id,
        "thread_name": "New Chat",
    }


@thread_router.patch("/{thread_id}/config")
async def update_thread_config(
    thread_id: str,
    body: UpdateThreadConfigRequest,
    user_id: str = Depends(authenticate_user),
    thread_repository: ThreadRepository = Depends(fetch_thread_repository),
):
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

    # Only fields actually sent by frontend
    update_data = body.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if "mcp_servers" in update_data:
        update_data["mcp_servers"] = [
            server.model_dump() if hasattr(server, "model_dump") else server
            for server in body.mcp_servers
        ]

    if not update_data:
        raise AppError(
            "No configuration provided",
            400,
            "NO_CONFIG_PROVIDED",
        )

    update_data["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
    

    result = await thread_repository.update_config(
        user_id=user_id,
        thread_id=thread_id,
        data=update_data,
    )

    return {
        "success": True,
        "message": "Thread configuration updated",
        "updated": update_data,
    }
