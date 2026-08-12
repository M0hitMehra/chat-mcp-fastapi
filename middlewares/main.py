import datetime
from time import timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
from fastapi.middleware.cors import CORSMiddleware


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
from dependencies.repositories import fetch_message_repository, fetch_summary_repository
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
from routes.auth_routes import auth_router
from routes.thread_routes import thread_router
from routes.session_routes import session_router

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
app.include_router(thread_router, prefix="/threads")
app.include_router(session_router, prefix="/sessions")


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
    print("history+history", history)
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
