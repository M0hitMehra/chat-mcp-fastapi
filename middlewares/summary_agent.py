from langchain_google_genai import ChatGoogleGenerativeAI

class SummaryAgent:
    def __init__(self, api_key: str):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite",  
            api_key=api_key,
        )

    def format_messages(self, messages: list, previous_summary: str = "") -> str:
        prompt = []

        # FIX: Inject previous summary to maintain long-term context
        if previous_summary:
            prompt.append(f"[PREVIOUS CONTEXT SUMMARY]:\n{previous_summary}\n")
            
        prompt.append("[NEW MESSAGES TO PROCESS]:")
        
        for msg in messages:
            role = msg.get("role", "UNKNOWN").upper()
            content = msg.get("content", "")
            
            # FIX: Safely handle tool calls/multimodal where content is a list instead of a string
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict):
                        text_parts.append(part.get("text", str(part)))
                    else:
                        text_parts.append(str(part))
                content = " ".join(text_parts)
            elif not isinstance(content, str):
                content = str(content)

            prompt.append(f"{role}: {content}")

        prompt.append(
            "\n[TASK]: Combine the [PREVIOUS CONTEXT SUMMARY] (if it exists) with the [NEW MESSAGES] "
            "into a single, updated, highly concise summary. Retain key entities, decisions, and context. "
            "Output ONLY the updated summary text, nothing else."
        )
        
        return "\n".join(prompt)