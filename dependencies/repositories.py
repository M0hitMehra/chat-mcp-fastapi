from repositories.user_repository import UserRepository
from repositories.thread_repositories import ThreadRepository
from repositories.message_repository import MessageRepository
from repositories.session_repository import SessionRepository


def fetch_user_repository():
    return UserRepository()


def fetch_thread_repository():
    return ThreadRepository()

def fetch_message_repository():
    return MessageRepository()

def fetch_session_repository():
    return SessionRepository()
