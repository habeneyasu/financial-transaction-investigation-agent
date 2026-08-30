from app.config.settings import settings
from app.llm.providers.gemini import GeminiProvider


class LLMClient:
    """Provider-independent interface for LLM calls."""

    def __init__(self):
        if settings.default_llm_provider != "gemini":
            raise ValueError(
                f"Unsupported LLM provider: {settings.default_llm_provider}"
            )

        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self._provider = GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return await self._provider.generate(
            system_prompt,
            user_prompt,
        )