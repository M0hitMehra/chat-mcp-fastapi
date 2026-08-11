from services.auth_service import AuthService
from dependencies.repositories import fetch_user_repository
from repositories.user_repository import UserRepository
from repositories.summary_repository import SummaryRepository
from repositories.message_repository import MessageRepository
from fastapi import Depends
from repositories.session_repository import SessionRepository
from services.chat_history_service import ChatHistoryService
from services.summary_service import SummaryService
from dependencies.repositories import fetch_message_repository, fetch_summary_repository
from summary_agent import SummaryAgent


def get_auth_service(repo: UserRepository = Depends(fetch_user_repository)):
    return AuthService(repo)


def get_session_repository():
    return SessionRepository()


def fetch_chat_history_service():
    return ChatHistoryService(fetch_message_repository())


def fetch_summary_service(
    api_key: str,
    summary_repository: SummaryRepository = Depends(fetch_summary_repository),
    message_repository: MessageRepository = Depends(fetch_message_repository),
):
    summary_agent: SummaryAgent = SummaryAgent(api_key=api_key)
    print("summary_repository_summary_repository",summary_repository)
    return SummaryService(
        summary_repository=summary_repository,
        message_repository=message_repository,
        summary_agent=summary_agent,
    )


def create_summary_service(
    api_key: str,
    summary_repository: SummaryRepository,
    message_repository: MessageRepository,
):
    summary_agent = SummaryAgent(api_key=api_key)

    return SummaryService(
        summary_repository=summary_repository,
        message_repository=message_repository,
        summary_agent=summary_agent,
    )