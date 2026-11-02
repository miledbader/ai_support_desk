from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from ai_support_desk.services import (
    AIConfigurationError,
    AIServiceError,
    SUPPORT_INSTRUCTIONS,
    generate_reply,
)


@pytest.fixture
def provider(monkeypatch):
    # These tests never contact OpenAI or use a real key.
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    constructor = MagicMock()
    monkeypatch.setattr("ai_support_desk.services.OpenAI", constructor)
    return constructor.return_value.__enter__.return_value


def test_generate_reply_uses_model_and_returns_text(provider):
    provider.responses.create.return_value = SimpleNamespace(
        output_text="  Try the password reset link.  "
    )

    assert generate_reply("I forgot my password") == "Try the password reset link."
    provider.responses.create.assert_called_once_with(
        model="test-model",
        instructions=SUPPORT_INSTRUCTIONS,
        input= [
            {"role": "user", "content": "I forgot my password"}
        ],
        max_output_tokens=500,
        store=False,
    )


@pytest.mark.parametrize("key", [None, "", "   "])
def test_generate_reply_requires_key(provider, monkeypatch, key):
    if key is None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    else:
        monkeypatch.setenv("OPENAI_API_KEY", key)

    with pytest.raises(AIConfigurationError):
        generate_reply("Hello")
    provider.responses.create.assert_not_called()


def test_generate_reply_rejects_blank_model(provider, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "   ")

    with pytest.raises(AIConfigurationError):
        generate_reply("Hello")
    provider.responses.create.assert_not_called()


def test_generate_reply_handles_provider_failure(provider, caplog):
    provider.responses.create.side_effect = OpenAIError("private provider details")

    with pytest.raises(AIServiceError):
        generate_reply("Hello")

    assert "type=OpenAIError" in caplog.text
    assert "private provider details" not in caplog.text
    assert "test-key" not in caplog.text


def test_generate_reply_rejects_empty_output(provider):
    provider.responses.create.return_value = SimpleNamespace(output_text="   ")

    with pytest.raises(AIServiceError):
        generate_reply("Hello")

def test_generate_reply_preserves_normal_text(provider):
    provider.responses.create.return_value = SimpleNamespace(
        output_text="Hello! How can I help?"
    )

    result = generate_reply("Hello")

    assert result == "Hello! How can I help?"