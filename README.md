# AI Support Desk

A learning project built with FastAPI, Pydantic, and the OpenAI Python SDK.
The current version answers individual support messages. It does not yet have
conversation memory, company documents, account access, or ticket creation.

## Run locally

Requires Python 3.12+ and uv. From the project directory:

```powershell
uv sync
Copy-Item .env.example .env
```

Open `.env` in your editor and set `OPENAI_API_KEY` to your own OpenAI API key.
Keep the key local; do not paste it into chat or commit it. `.env` is ignored by
Git. `OPENAI_MODEL` selects the model; the example uses `gpt-4.1-mini`.
Your API account needs access to the selected model and available API billing
or credits. Live requests use the OpenAI API and may incur charges.

Start the app (the environment file is loaded by Uvicorn):

```powershell
uv run uvicorn ai_support_desk.api:app --reload --env-file .env
```

Visit http://127.0.0.1:8000/docs and try `POST /chat`:

```json
{"message": "How can I reset my password?"}
```

## Request flow

1. `api.py` receives `POST /chat`.
2. `schemas.py` validates and trims the message using `ChatRequest`.
3. `services.py` reads configuration and calls the OpenAI Responses API with
   support instructions and the user's message.
4. The service returns `response.output_text` as a string.
5. The route wraps it in `ChatResponse`, which FastAPI serializes to JSON.

Each call is independent. The response is capped at 500 output tokens and the
SDK request timeout is 30 seconds with automatic retries disabled.

## Errors

- `422`: invalid request body, such as a blank or oversized message.
- `503`: missing API key or a blank model setting.
- `502`: provider failure or an empty AI response.

Provider error details are not returned to clients. `GET /health` reports that
the web app is running; it does not check OpenAI connectivity or credentials.

## Tests

```powershell
uv run pytest -v
```

Tests simulate the AI provider using mocks, so no API key, network access, or
paid model calls are needed. Route tests check validation, JSON responses, and
error handling. Service tests check the model request and provider failures.

SDK reference: https://developers.openai.com/api/reference/python
