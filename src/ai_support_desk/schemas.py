from pydantic import BaseModel, ConfigDict, Field

class ChatRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra= "forbid",
        )
    message: str = Field(min_length=1, max_length=2000)
    conversation_id : str | None = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str