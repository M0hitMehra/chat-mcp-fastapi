from repositories.summary_repository import SummaryRepository
from bson import ObjectId
from summary_agent import SummaryAgent
from repositories.message_repository import MessageRepository
from datetime import datetime, timezone
from pydantic import Field


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
        previous_summary = await self.summary_repository.find_by_thread(
           thread_id= thread_id,
           user_id= ObjectId(user_id),
        )
        return previous_summary

    async def update_summary_if_needed(
        self, thread_id: str, user_id: ObjectId, summary: str
    ):

        # create summary

        agent = self.summary_agent
        summary.append(
            {"role": "Task", "content": "Summarize the all message in least characters"}
        )
        print("summary_summa", summary[-1])

        formatted_messages = self.summary_agent.format_messages(summary)

        # 2. Generate summary using the agent
        response = await self.summary_agent.model.ainvoke(input=formatted_messages)

        # 3. Extract summary content from response
        summary_content = self._extract_response_content(response)

        # 4. Get the last message ID from the list
        last_message_id = summary[-2].get("_id")
        if isinstance(last_message_id, ObjectId):
            last_message_id = str(last_message_id)

        # 5. Prepare data for saving
        data = {
            "thread_id": thread_id,
            "user_id": ObjectId(user_id),
            "content": summary_content,  # Store the summary text
            "last_summarized_message_id": last_message_id,
            "created_at":   datetime.now(timezone.utc),
            "updated_at":  datetime.now(timezone.utc)
        }

        # 6. Check if summary already exists
        existing = await self.summary_repository.find_by_thread(thread_id, user_id)

        # 7. Save or update
        if existing:
            await self.summary_repository.update(thread_id, user_id, data)
        else:
            await self.summary_repository.create(data)

        return data

    def _extract_response_content(self, response) -> str:
        """
        Extract text content from the agent's response.

        Handles different response types from LangChain.
        """
        # If response is a string
        if isinstance(response, str):
            return response

        # If response has a content attribute (AIMessage)
        if hasattr(response, "content"):
            content = response.content

            # If content is a list (multimodal response)
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict):
                        # Extract text from dict
                        text_parts.append(part.get("text", ""))
                    elif isinstance(part, str):
                        text_parts.append(part)
                return " ".join(text_parts)

            # If content is a string
            elif isinstance(content, str):
                return content

            # Fallback
            return str(content)

        # If response is a dict
        if isinstance(response, dict):
            return response.get("content", str(response))

        # Last resort
        return str(response)
