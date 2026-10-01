from google import genai
from google.genai import types


class GeminiProvider:
    """Gemini LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
    ):
        self._client = genai.Client(
            api_key=api_key
        )
        self._model = model
        self._temperature = temperature

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        chat = self._client.aio.chats.create(
            model=self._model,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=self._temperature,
            ),
        )

        response = await chat.send_message(
            user_prompt
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text