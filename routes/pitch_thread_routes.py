
from fastapi.routing import APIRouter
from langchain_core.messages import HumanMessage

import datetime

from schemas import (
    CreatePitchThreadRequest,
    UpdateThreadConfigRequest,
    CompanySearchResponse,
    CompanySearchResult
    
     
)
from utils.errorHandler.error_handler import AppError

from fastapi import Depends
from middlewares.authenticate_user import authenticate_user
from dependencies.repositories import fetch_pitch_thread_repository
from repositories.pitch_thread_respository import PitchThreadRepository
from repositories.message_repository import MessageRepository
from dependencies.repositories import fetch_message_repository

from fastapi.responses import JSONResponse


import time








import datetime
from fastapi.responses import StreamingResponse
import json
 

from schemas import (
    ChatRequest,
     UpdateThreadConfigRequest,
)
from utils.errorHandler.error_handler import AppError

from agent import create_chat_agent_for_pitch , create_company_selector_agent
from fastapi import Depends
from middlewares.authenticate_user import authenticate_user
from repositories.thread_repositories import ThreadRepository
from repositories.message_repository import MessageRepository
from dependencies.repositories import fetch_message_repository, fetch_summary_repository
from dependencies.services import (
    fetch_chat_history_service,
    ChatHistoryService,
    create_summary_service,
)
import uuid
from repositories.summary_repository import SummaryRepository

 

import uuid

from bson import ObjectId

pitch_thread_router = APIRouter()


@pitch_thread_router.get("/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    limit: int =30,
    skip: int=0,
    user_id: str = Depends(authenticate_user),
    thread_repository: PitchThreadRepository = Depends(fetch_pitch_thread_repository),
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
        limit=limit,
        skip=skip,
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


@pitch_thread_router.get("/")
async def get_threads(
    user_id: str = Depends(authenticate_user),
    thread_repository: PitchThreadRepository = Depends(fetch_pitch_thread_repository),
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


@pitch_thread_router.post("/")
async def create_thread(
    body: CreatePitchThreadRequest,
    user_id: str = Depends(authenticate_user),
    thread_repository: PitchThreadRepository = Depends(fetch_pitch_thread_repository),
):
     

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
            
            "pitch_type":body.pitch_info.pitch_type,
            "cin":body.pitch_info.cin,
            "companyName":body.pitch_info.companyName,
            "contact":body.pitch_info.contact,
            "email":body.pitch_info.email,
            "phone":body.pitch_info.phone,
            "pitch_description":body.pitch_info.pitch_description
        }
    )

    return {
        "thread_id": thread_id,
        "thread_name": "New Chat",
    }


 
@pitch_thread_router.patch("/{thread_id}/config")
async def update_thread_config(
    thread_id: str,
    body: UpdateThreadConfigRequest,
    user_id: str = Depends(authenticate_user),
    thread_repository: PitchThreadRepository = Depends(fetch_pitch_thread_repository),
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



@pitch_thread_router.get("/latest")
async def get_latest_pitch_thread(
    user_id: str = Depends(authenticate_user),
    thread_repository: PitchThreadRepository = Depends(fetch_pitch_thread_repository),
):
    thread =  await thread_repository.find_latest_pitch_thread_by_user_id(user_id=user_id)
    return {
            "success": True,
            "message": "Latest thread fetched",
            "data": thread,
        }
    

async def stream_response(
    agent, config, message, user_id, thread_id , message_repository, history
):
    assistant_content = ""
    messages = [*history, HumanMessage(content=message)]


    try:
        async for chunk, _ in agent.astream(
            {"messages": messages},
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


@pitch_thread_router.post("/chat")
async def chat(
    body: ChatRequest,
    user_id: str = Depends(authenticate_user),
    message_repository: MessageRepository = Depends(fetch_message_repository),
    thread_repository: ThreadRepository = Depends(fetch_pitch_thread_repository),
    historyService: ChatHistoryService = Depends(fetch_chat_history_service),
    summary_repository: SummaryRepository = Depends(fetch_summary_repository),
):

    thread = await thread_repository.find_by_user_id_and_thread_id(
        thread_id=body.thread_id, user_id=user_id
    )
    print("--------------------------")
    print(user_id)
    print(body)
    print(thread)
    
    if(thread is None):
        raise AppError(
            "Thread does not exist for user",
            404,
            "INVALID_THREAD"
        )

    if(thread["cin"] is None) :
         raise AppError(
                    "cin not found",
                    404,
                    "CIN_NOT_FOUND",
                )

    summar_service = create_summary_service(
        api_key=thread["api_key"],
        message_repository=message_repository,
        summary_repository=summary_repository,
    )
 

    thread_id = body.thread_id

    await message_repository.create(
        {
            "user_id": ObjectId(user_id),
            "thread_id": thread_id,
            "role": "user",
            "content": body.message,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
    )

    history = await historyService.build_history(
        thread_id=thread_id, user_id=user_id, summar_service=summar_service
    )


    agent = await create_chat_agent_for_pitch(
        model_name=thread["model_name"] or "gemini-3.1-flash-lite",
        api_key=thread["api_key"],
        mcp_servers=thread["mcp_servers"] or [],
        llm_name="gemini",
        
         company_name=thread["companyName"],   # ← add these
    cin=thread["cin"],
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
            message_repository=message_repository,
            history=history,
        ),
        media_type="text/event-stream",
    )




async def stream_response_for_companySelection(
    agent, config, message, user_id 
):
    
    messages = [  HumanMessage(content=message)]

    assistant_content = ""

    try:
        async for chunk, _ in agent.astream(
            {"messages":messages },
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

         

        yield "data: [DONE]\n\n"

    except Exception as e:

        print("Streaming error:", e)

        yield f"data: {json.dumps({
            'error': str(e)
        })}\n\n"

        yield "data: [DONE]\n\n"




import certifi
import httpx

CORPVUE_SEARCH_URL = (
    "https://www.corpvue.com/gateway/cometsearch/open/searchcompanyorllp"
)

@pitch_thread_router.post("/company-search")
async def search_corpvue(company_name: str) -> list[dict]:
    async with httpx.AsyncClient(
        timeout=30.0,
        verify=False,
    ) as client:
        response = await client.get(
            CORPVUE_SEARCH_URL,
            params={"query": company_name.strip()}
        )
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Unexpected response from CorpVue")

        return data
    
import ssl
 

@pitch_thread_router.get("/debug/corpvue-ssl")
async def debug_corpvue_ssl():
    result = {
        "openssl": ssl.OPENSSL_VERSION,
        "certifi_path": certifi.where(),
        "default_verify_paths": str(ssl.get_default_verify_paths()),
    }

    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            verify=certifi.where(),
        ) as client:
            response = await client.get("https://www.corpvue.com/")
            result["http_status"] = response.status_code
    except Exception as exc:
        result["request_error"] = f"{type(exc).__name__}: {exc}"

    return result
