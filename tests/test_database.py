from ai_support_desk.database import (
    initialize_database,
    save_message,
    get_messages
)

def test_messages_are_saved_by_conversation(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "ai_support_desk.database.DATABASE_PATH",
        tmp_path / "test.db",
    )
    initialize_database()
    save_message("conversation-1", "user", "Hello")
    save_message("conversation-1", "assistant", "How can I help?")
    save_message("conversation-2", "user", "A different conversation")

    messages = get_messages("conversation-1")
    assert messages == [
        {"role" : "user", "content":"Hello"},
        {"role" : "assistant", "content": "How can I help?"},
    ]