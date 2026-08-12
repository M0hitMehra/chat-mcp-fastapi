from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from repositories.message_repository import MessageRepository
from services.summary_service import SummaryService

class ChatHistoryService:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def build_history(self, thread_id: str, user_id: str, summar_service: SummaryService):
        previous_summary = await summar_service.fetch_previous_summary(
            thread_id=thread_id, user_id=user_id
        )

        last_msg_id = previous_summary.get("last_summarized_message_id") if previous_summary else None

        messages = await self.message_repository.find_messages_after_summary(
            thread_id=thread_id,
            user_id=user_id,
            last_message_id=last_msg_id
        )

        if len(messages) > 48:
            # This will now correctly merge old + new context
            await summar_service.update_summary_if_needed(
                thread_id=thread_id, user_id=user_id, new_messages=messages
            )
            # Re-fetch the newly updated summary to use in the current prompt
            previous_summary = await summar_service.fetch_previous_summary(
                thread_id=thread_id, user_id=user_id
            )

        history = []
        summary_text = previous_summary.get("content", "") if previous_summary else ""
        
        if summary_text:
            history.append(
                SystemMessage(
                    content=f"Previous conversation summary: {summary_text}\n\n"
                            "Continue the conversation based on the above context."
                )
            )

        for message in messages:
            if message["role"] == "user":
                history.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                content = message.get("content", "")
                if isinstance(content, list):
                    text_content = " ".join([p.get("text", str(p)) if isinstance(p, dict) else str(p) for p in content])
                    history.append(AIMessage(content=text_content))
                else:
                    history.append(AIMessage(content=content))

        return history