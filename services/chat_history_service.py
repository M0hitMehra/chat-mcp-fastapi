from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from repositories.message_repository import MessageRepository
from services.summary_service import SummaryService


class ChatHistoryService:

    def __init__(
        self,
        message_repository: MessageRepository,
    ):
        self.message_repository = message_repository

    async def build_history(
        self,
        thread_id: str,
        user_id: str,
        summar_service: SummaryService,
    ):

        previous_summary = await summar_service.fetch_previous_summary(
            thread_id=thread_id, user_id=user_id
        )

        messages = await self.message_repository.find_messages_after_summary(
            thread_id=thread_id,
            user_id=user_id,
            last_message_id=(
                previous_summary.get("last_summarized_message_id") if previous_summary else None
            ),
        )
        print("last_summarized_message_id_last_summarized_message_id", previous_summary)

        if len(messages) > 48:
            # raise Exception
            await summar_service.update_summary_if_needed(
                thread_id=thread_id, user_id=user_id, summary=messages
            )

        history = []

        history.append(
            SystemMessage(
                content=f"Previous conversation summary: {(previous_summary["content"] if previous_summary else "")}\n\n"
                "Continue the conversation based on the above context."
            )
        )

        for message in messages:

            if message["role"] == "user":

                history.append(HumanMessage(content=message["content"]))

            elif message["role"] == "assistant":

                history.append(AIMessage(content=message["content"]))

        return history
