from langchain_google_genai import ChatGoogleGenerativeAI


class SummaryAgent:

    def __init__(
        self,
        api_key: str,
    ):

        self.model = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite",
            api_key=api_key,
        )

    def format_messages(self,messages):

        prompt = []

        for msg in messages:

            role = msg["role"].upper()

            prompt.append(f"{role}\n{msg['content']}")

        return "\n\n-----------------\n\n".join(prompt)
