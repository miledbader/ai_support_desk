import logging
import os

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

SUPPORT_INSTRUCTIONS = (
    "You are a helpful support desk assistant. Give clear, concise guidance. "
    "Ask a clarifying question when needed. Do not invent company policies, "
    "claim access to customer accounts, or claim to have performed actions. "
    "Never ask for passwords or secret credentials."
)


class AIConfigurationError(Exception):
    """The server is missing configuration needed for AI replies."""


class AIServiceError(Exception):
    """The AI provider failed to return a usable reply."""


def generate_reply(message: str,
                   history: list[dict[str, str]] | None = None
                   ) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIConfigurationError("OPENAI_API_KEY is not configured.")

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    if not model:
        raise AIConfigurationError("OPENAI_MODEL cannot be blank.")

    messages = history.copy() if history is not None else []
    messages.append({"role": "user", "content": message})

    try:
        with OpenAI(api_key=api_key, timeout=30.0, max_retries=0) as client:
            response = client.responses.create(
                model=model,
                instructions=SUPPORT_INSTRUCTIONS,
                input=messages,
                max_output_tokens=500,
                store=False,
            )
    except OpenAIError as exc:
        # Log diagnostic identifiers, never the key, message, or raw error body.
        logger.warning(
            "AI request failed: type=%s status=%s code=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
            getattr(exc, "code", None),
        )
        raise AIServiceError("The AI provider request failed.") from exc

    reply = response.output_text.strip()
    if not reply:
        logger.warning("AI request returned no text output.")
        raise AIServiceError("The AI provider returned an empty reply.")
    return reply
