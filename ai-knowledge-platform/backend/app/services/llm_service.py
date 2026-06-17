"""LLM service - wraps calls to OpenAI-compatible LLM APIs with dynamic model support."""
import httpx
from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()

# Default timeout: 10s connect, 60s read
DEFAULT_TIMEOUT = httpx.Timeout(10.0, read=60.0, write=10.0, connect=10.0)


class LLMService:
    """Encapsulates LLM API calls with support for dynamic model switching.

    Usage:
      svc = LLMService(model_config)   # model_config = {base_url, api_key, model_name}
      svc = LLMService()               # use default from settings
    """

    def __init__(self, model_config: dict | None = None):
        cfg = model_config or {}
        self.base_url = cfg.get("base_url") or settings.LLM_BASE_URL
        self.api_key = cfg.get("api_key") or settings.LLM_API_KEY
        self.model = cfg.get("model_name") or settings.LLM_MODEL_NAME
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key, timeout=DEFAULT_TIMEOUT, max_retries=1)

    def chat(self, messages: list[dict], max_tokens: int = None,
             temperature: float = None, stream: bool = False):
        """Send a chat completion request."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
                temperature=temperature or settings.LLM_TEMPERATURE,
                stream=stream,
            )
            return response
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {str(e)}")

    def chat_stream(self, messages: list[dict], max_tokens: int = None,
                    temperature: float = None):
        """Stream chat completion tokens. Raises on error so caller can handle it."""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
            temperature=temperature or settings.LLM_TEMPERATURE,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
