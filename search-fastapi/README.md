## Search FastAPI - WebSocket + OpenAI Streaming

### Prerequisites
- Python 3.10+

### Setup
1. Create and activate a virtual environment.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set your OpenAI API key (recommended via .env):
   - Create a `.env` file with:
```bash
OPENAI_API_KEY=sk-REPLACE_ME
```

### Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test client
- Open `http://localhost:8000/` to use the included HTML client.
- It connects to the WebSocket at `/ws`, sends the topic, and streams the response.

### WebSocket contract
- Client sends either plain text (topic) or JSON: `{ "topic": "..." }`.
- Server sends JSON frames in this structure: `{ "message": string, "data": object, "status": "success" | "error" }`.
  - On start:
    ```json
    { "message": "started", "data": {}, "status": "success" }
    ```
  - For each streamed chunk:
    ```json
    { "message": "chunk", "data": { "text": "..." }, "status": "success" }
    ```
  - On completion:
    ```json
    { "message": "completed", "data": { "final": true }, "status": "success" }
    ```
  - On error:
    ```json
    { "message": "<error message>", "data": {}, "status": "error" }
    ```

### HTTP endpoint (non-streaming)
- `POST /generate`
  - Request body:
    ```json
    { "topic": "alternative medicine" }
    ```
  - Response body:
    ```json
    { "message": "completed", "data": { "text": "..." }, "status": "success" }
    ```

### Notes
- CORS is permissive for demo purposes. Restrict origins in production.
- The system prompt is embedded in `app/main.py` as provided.
