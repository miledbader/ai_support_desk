from fastapi import FastAPI, HTTPException
from ai_support_desk.schemas import ChatRequest, ChatResponse
from ai_support_desk.services import (
    AIConfigurationError,
    AIServiceError,
    generate_reply,
)
from uuid import uuid4
from ai_support_desk.database import (
    initialize_database,
    save_message,
    get_messages,
)

app = FastAPI(title="AI Support Desk")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversation_id or str(uuid4())
    history = get_messages(conversation_id)
    try:
        reply = generate_reply(request.message, history=history)
    except AIConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI replies are not configured on the server.",
        ) from exc
    except AIServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to get an AI reply. Please try again later.",
        ) from exc
    save_message(conversation_id, "user", request.message)
    save_message(conversation_id, "assistant", reply)
    return ChatResponse(
        reply=reply,
        conversation_id = conversation_id,
    )
