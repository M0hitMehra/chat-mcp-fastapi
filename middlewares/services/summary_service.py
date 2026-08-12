from repositories.summary_repository import SummaryRepository
from bson import ObjectId
from summary_agent import SummaryAgent
from repositories.message_repository import MessageRepository
from datetime import datetime, timezone


class SummaryService:
    def __init__(
        self,
        summary_repository: SummaryRepository,
        message_repository: MessageRepository,
        summary_agent: SummaryAgent,
    ):
        self.summary_repository = summary_repository
        self.message_repository = message_repository
        self.summary_agent = summary_agent

    async def fetch_previous_summary(self, thread_id: str, user_id: ObjectId):
        return await self.summary_repository.find_by_thread(
            thread_id=thread_id, user_id=user_id
        )

    async def update_summary_if_needed(
        self, thread_id: str, user_id: ObjectId, new_messages: list
    ):
        # FIX: Fetch the EXISTING summary from DB to pass to the agent (Fixes Context Loss)
        existing = await self.summary_repository.find_by_thread(thread_id, user_id)
        previous_summary_text = existing.get("content", "") if existing else ""

        # Format messages with the old summary included
        formatted_messages = self.summary_agent.format_messages(
            new_messages, previous_summary_text
        )

        # Generate merged summary
        response = await self.summary_agent.model.ainvoke(input=formatted_messages)
        summary_content = self._extract_response_content(response)

        # Safely get the last message ID
        last_message_id = new_messages[-1].get("_id") if new_messages else None
        if isinstance(last_message_id, ObjectId):
            last_message_id = str(last_message_id)

        data = {
            "thread_id": thread_id,
            "user_id": ObjectId(user_id),
            "content": summary_content,
            "last_summarized_message_id": last_message_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        if existing:
            await self.summary_repository.update(thread_id, user_id, data)
        else:
            await self.summary_repository.create(data)

        return data

    def _extract_response_content(self, response) -> str:
        if hasattr(response, "content"):
            content = response.content
            if isinstance(content, list):
                return " ".join(
                    [
                        p.get("text", str(p)) if isinstance(p, dict) else str(p)
                        for p in content
                    ]
                )
            return str(content)
        return str(response)
