from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from ai_support_desk.api import app
from ai_support_desk.services import AIConfigurationError, AIServiceError
from ai_support_desk.database import initialize_database

client = TestClient(app)


@pytest.fixture
def reply_generator(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "ai_support_desk.database.DATABASE_PATH",
        tmp_path / "test.db"
    )
    initialize_database()
    generator = Mock(return_value="Here is some support guidance.")
    monkeypatch.setattr("ai_support_desk.api.generate_reply", generator)
    return generator

def test_client_rejects_blank_message():
    response = client.post("/chat", json= {"message": "   "})

    assert response.status_code == 422 #

def test_chat_trims_message(reply_generator):
    response = client.post("/chat", json={"message": "  Hello  "})

    assert response.status_code == 200
    assert response.json()["reply"] == "Here is some support guidance."
    assert response.json()["conversation_id"]
    reply_generator.assert_called_once_with("Hello", history=[])


def test_chat_rejects_message_over_limit():
    response = client.post("/chat", json={"message": "a" * 2001})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "message"]
    assert response.json()["detail"][0]["type"] == "string_too_long"


def test_chat_exact_message_limit(reply_generator):
    message = "a" * 2000
    response = client.post("/chat", json= {"message": message})
    assert response.status_code == 200
    assert response.json()["reply"] == "Here is some support guidance."
    assert response.json()["conversation_id"]
    reply_generator.assert_called_once_with(message, history=[])

def test_health_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize(
    "error, status, detail",
    [
        (AIConfigurationError("private configuration"), 503,
         "AI replies are not configured on the server."),
        (AIServiceError("private provider details"), 502,
         "Unable to get an AI reply. Please try again later."),
    ],
)
def test_chat_returns_safe_error(reply_generator, error, status, detail):
    reply_generator.side_effect = error

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == status
    assert response.json() == {"detail": detail}

def test_chat_accepts_conversation_id(reply_generator):
    response = client.post(
        "/chat",
        json = {"message": "The reset link expired",
                "conversation_id": "conversation-123",}
    )
    assert response.status_code == 200
    reply_generator.assert_called_once_with(
        "The reset link expired",
        history=[],
        )
    assert response.json()["conversation_id"] == "conversation-123"