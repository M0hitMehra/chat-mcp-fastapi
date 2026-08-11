import datetime
from time import timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import auth_router

from schemas import (
    ConnectRequest,
    ConnectResponse,
    ChatRequest,
    CreateThreadRequest,
    UpdateThreadConfigRequest,
)
from utils.errorHandler.exception_handlers import app_error_handler
from utils.errorHandler.error_handler import AppError

from agent import create_chat_agent
from fastapi import Depends
from middlewares.authenticate_user import authenticate_user
from dependencies.repositories import fetch_session_repository
from repositories.session_repository import SessionRepository
from dependencies.repositories import fetch_thread_repository
from repositories.thread_repositories import ThreadRepository
from repositories.message_repository import MessageRepository
from dependencies.repositories import fetch_message_repository,fetch_summary_repository
from dependencies.services import (
    fetch_chat_history_service,
    ChatHistoryService,
    SummaryService,
    fetch_summary_service,
    create_summary_service,
)
import uuid
from repositories.summary_repository import SummaryRepository

from bson import ObjectId
import os

app = FastAPI(
    title="MCP Chat Backend",
    version="1.0.0",
)

app.add_exception_handler(AppError, app_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth")


@app.get("/health", dependencies=[Depends(authenticate_user)])
async def health():

    return {"status": "ok", "message": "Backend Running"}


@app.post("/connect", response_model=ConnectResponse)
async def connect(
    user_id: str = Depends(authenticate_user),
    session_repository: SessionRepository = Depends(fetch_session_repository),
):

    session_id = str(uuid.uuid4())

    session_document = {
        "session_id": session_id,
        "user_id": ObjectId(user_id),
        # "mcp_servers": [server.model_dump() for server in body.mcp_servers],
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }

    await session_repository.create(session_document)

    return {"session_id": session_id}


async def stream_response(
    agent, config, message, user_id, thread_id, session_id, message_repository, history
):
    assistant_content = ""

    try:
        async for chunk, _ in agent.astream(
            {"messages": history},
            config,
            stream_mode="messages",
        ):
            content = chunk.content

            if isinstance(content, str):

                if content:
                    assistant_content += content

                    yield f"data: {json.dumps({'token': content})}\n\n"

            elif isinstance(content, list):

                for part in content:

                    if isinstance(part, str):

                        if part:
                            assistant_content += part

                            yield f"data: {json.dumps({'token': part})}\n\n"

                    elif isinstance(part, dict):

                        if part.get("type") == "text":

                            text = part.get("text", "")

                            if text:
                                assistant_content += text

                                yield f"data: {json.dumps({'token': text})}\n\n"

        if assistant_content:

            await message_repository.create(
                {
                    "user_id": ObjectId(user_id),
                    "thread_id": thread_id,
                    "session_id": session_id,
                    "role": "assistant",
                    "content": assistant_content,
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                }
            )

        yield "data: [DONE]\n\n"

    except Exception as e:

        print("Streaming error:", e)

        yield f"data: {json.dumps({
            'error': str(e)
        })}\n\n"

        yield "data: [DONE]\n\n"


@app.post("/chat")
async def chat(
    body: ChatRequest,
    user_id: str = Depends(authenticate_user),
    message_repository: MessageRepository = Depends(fetch_message_repository),
    session_manager: SessionRepository = Depends(fetch_session_repository),
    thread_repository: ThreadRepository = Depends(fetch_thread_repository),
    historyService: ChatHistoryService = Depends(fetch_chat_history_service),
    summary_repository: SummaryRepository = Depends(fetch_summary_repository),
):

    thread = await thread_repository.find_by_user_id_and_thread_id(
        thread_id=body.thread_id, user_id=user_id
    )

    summar_service = create_summary_service(
        api_key=thread["api_key"],
        message_repository=message_repository,
        summary_repository=summary_repository,
    )

    session_id = thread["session_id"]
    session = await session_manager.find_user_session(
        session_id=session_id, user_id=user_id
    )

    if not session:
        raise AppError(
            "Session not found",
            404,
            "INVALID_SESSION",
        )

    thread_id = body.thread_id

    # Save user message
    await message_repository.create(
        {
            "user_id": ObjectId(user_id),
            "thread_id": thread_id,
            "session_id": body.session_id,
            "role": "user",
            "content": body.message,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
    )

    history = await historyService.build_history(
        thread_id=thread_id, user_id=user_id, summar_service=summar_service
    )

    # build agent or reuse agent

    agent = await create_chat_agent(
        model_name=thread["model_name"] or "gemini-3.1-flash-lite",
        api_key=thread["api_key"],
        mcp_servers=thread["mcp_servers"] or [],
    )

    config = {"configurable": {"thread_id": thread_id}}
    print("history+history",history)
    # raise Exception
    return StreamingResponse(
        stream_response(
            agent=agent,
            config=config,
            message=body.message,
            user_id=user_id,
            thread_id=thread_id,
            session_id=body.session_id,
            message_repository=message_repository,
            history=history,
        ),
        media_type="text/event-stream",
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):

    deleted = session_manager.delete(session_id)

    if not deleted:

        raise AppError("No Seesion exist with this session_id", 402, "INVALID_SESSION")

    return {"message": "Session Deleted"}


@app.get("/sessions")
async def get_sessions(
    user_id: str = Depends(authenticate_user),
    session_repository: SessionRepository = Depends(fetch_session_repository),
):
    sessions = await session_repository.find_by_user_id(user_id)

    for session in sessions:
        session["_id"] = str(session["_id"])

    return {
        "success": True,
        "data": sessions,
    }


@app.get("/threads/{thread_id}/messages")
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


@app.get("/threads")
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


@app.post("/threads")
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


@app.patch("/threads/{thread_id}/config")
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
