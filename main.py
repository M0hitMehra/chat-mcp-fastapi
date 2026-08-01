from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
from fastapi.middleware.cors import CORSMiddleware
# from backend import agent
from schemas import (
    ConnectRequest,
    ConnectResponse,
    ChatRequest,
)

from session import session_manager
from agent import create_chat_agent

app = FastAPI(
    title="MCP Chat Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "message": "Backend Running",
    }


@app.post(
    "/connect",
    response_model=ConnectResponse,
)
async def connect(body: ConnectRequest):

    try:
        print(
            f"Connecting to MCP with API Key: {body.api_key}, Model: {body.model}, Thread ID: {body.thread_id}, MCP Servers: {body.mcp_servers}"
        )
        agent = await create_chat_agent(
            api_key=body.api_key,
            model_name=body.model,
            mcp_servers=body.mcp_servers,
        )
        print(f"Agent created: {agent}")
        config = {"configurable": {"thread_id": body.thread_id}}

        session_id = session_manager.create(
            agent=agent,
            config=config,
        )
        print(f"Session created with ID: {session_id}")
        return ConnectResponse(
            session_id=session_id,
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


async def stream_response(agent, config, message):

    async for chunk, _ in agent.astream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        },
        config=config,
        stream_mode="messages",
    ):

        content = chunk.content

        if isinstance(content, str):

            yield f"data: {json.dumps({'token': content})}\n\n"

        elif isinstance(content, list):

            for part in content:

                if isinstance(part, str):

                    yield f"data: {json.dumps({'token': part})}\n\n"

                elif isinstance(part, dict):

                    if part.get("type") == "text":

                        text = part.get("text")

                        if text:

                            yield f"data: {json.dumps({'token': text})}\n\n"

    yield "data: [DONE]\n\n"


@app.post("/chat")
async def chat(body: ChatRequest):

    session = session_manager.get(body.session_id)

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Invalid Session",
        )

    return StreamingResponse(
        stream_response(
            session["agent"],
            session["config"],
            body.message,
        ),
        media_type="text/event-stream",
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):

    deleted = session_manager.delete(session_id)

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {"message": "Session Deleted"}


@app.get("/sessions")
async def sessions():

    return {
        "total": len(session_manager.list_sessions()),
        "sessions": session_manager.list_sessions(),
    }
