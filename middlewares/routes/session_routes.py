from fastapi.routing import APIRouter

from utils.errorHandler.error_handler import AppError

from fastapi import Depends
from middlewares.authenticate_user import authenticate_user
from dependencies.repositories import fetch_session_repository
from repositories.session_repository import SessionRepository
from dependencies.repositories import fetch_session_repository
 
session_router = APIRouter()




@session_router.delete("/{session_id}")
async def delete_session(session_id: str,session_manager :SessionRepository  = Depends(fetch_session_repository) ):

    deleted = session_manager.delete(session_id)

    if not deleted:

        raise AppError("No Seesion exist with this session_id", 402, "INVALID_SESSION")

    return {"message": "Session Deleted"}


@session_router.get("/")
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

