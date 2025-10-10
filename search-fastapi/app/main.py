import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

# Load environment variables from a local .env if present
load_dotenv()

# Instantiate OpenAI client (reads OPENAI_API_KEY from env)
openai_client = OpenAI()

# Provided system prompt
SYSTEM_PROMPT = (
	"""
	# Market Idea Expander

	## Your mission:

	You are a business strategy and market segmentation expert tasked with generating a list of markets, categories, niches or subniches across three core markets: Health, Wealth, and Relationships. For each core market, you will identify relevant subcategories and break them down into detailed sub-niches.

	### How to respond based on the user's prompt

	- If the user asks for **random ideas**, generate potential categories, subcategories, niches and sub-niches across all three markets (Health, Wealth, and Relationships).
	- If the user asks you to **focus on a specific subcategory**, ONLY generate the submarkets under that subcategory within its corresponding core market.

	For example:

	- If the user asks you to focus on "alternative medicine", Start with "alternative medicine" (subcategory within the Health market) as the first step in the hierarchy of your output and only provide subcategories underneath this one. Do not mention Wealth or Relationships in this case.

	## Output format

	Your output will contain only the answer, nothing before, nothing after.

	The output should follow this structure:

	{
	"Core Market": {
	  "Category (as many as you can)": {
	   "Subcategory (as many as you can)": {
	    "Niche (as many as you can)": {
	     "Sub-Niche (as many as you can)": {}
	}
	}
	}
	}
	}

	## Important rules

	- The categories must be based on the core markets Health, Wealth, and Relationships.
	- If a specific area of focus is requested by the user (e.g., alternative medicine), ONLY provide subcategories and niches underneath it
	- Always provide as many potential categories, subcategories, niches and sub-niches as you can
	- Avoid overlap between categories, subcategories, niches and sub-niches; each should be unique to its sub-niche.
	"""
)

app = FastAPI(title="Search WebSocket API")

# CORS: allow all for demo; restrict in production
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Serve static client
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(STATIC_DIR):
	app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> Any:
	index_path = os.path.join(STATIC_DIR, "index.html")
	if os.path.isfile(index_path):
		return FileResponse(index_path)
	return JSONResponse({"message": "Server is running. Open /static/index.html for the test client."})


@app.get("/health")
def health() -> Dict[str, str]:
	return {"status": "ok"}


def _extract_topic(payload_text: str) -> str:
	"""Parse the first client message; accept raw text or JSON with {"topic": "..."}."""
	text = payload_text.strip()
	if not text:
		return "random ideas"
	try:
		obj = json.loads(text)
		if isinstance(obj, dict) and obj.get("topic"):
			return str(obj["topic"]).strip() or "random ideas"
	except json.JSONDecodeError:
		pass
	return text


async def _send_json(ws: WebSocket, message: str, data: Optional[dict] = None, status: str = "success") -> None:
	"""Uniform WS response format: {"message": str, "data": {...}, "status": "success"|"error"}."""
	payload = {
		"message": message,
		"data": data or {},
		"status": status,
	}
	await ws.send_text(json.dumps(payload))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
	await websocket.accept()
	try:
		first_message = await websocket.receive_text()
		topic = _extract_topic(first_message)

		await _send_json(websocket, message="started")

		messages = [
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": topic},
		]

		# Stream tokens from OpenAI and forward to the WebSocket client
		stream = openai_client.chat.completions.create(
			model="gpt-4o-mini",
			messages=messages,  # type: ignore
			stream=True,
			temperature=0.7,
		)

		for chunk in stream:
			try:
				delta = chunk.choices[0].delta
				text_delta: Optional[str] = getattr(delta, "content", None)  # type: ignore
				if text_delta:
					await _send_json(
						websocket,
						message="chunk",
						data={"text": text_delta},
						status="success",
					)
			except RuntimeError:
				# Socket already closed
				break

		# Signal completion to client
		await _send_json(websocket, message="completed", data={"final": True}, status="success")

	except WebSocketDisconnect:
		# Client disconnected; nothing to do
		return
	except Exception as exc:  # noqa: BLE001
		try:
			await _send_json(websocket, message=str(exc), data={}, status="error")
		except Exception:
			pass
	finally:
		try:
			await websocket.close()
		except Exception:
			pass


@app.post("/generate")
async def generate(body: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Accepts JSON: { "topic": "..." }
	Returns one final response (non-streaming) in the required shape:
	{ "message": "completed", "data": { "text": "..." }, "status": "success" }
	"""
	topic = ""
	if isinstance(body, dict) and body.get("topic"):
		topic = str(body["topic"]).strip()
	if not topic:
		topic = "random ideas"

	messages = [
		{"role": "system", "content": SYSTEM_PROMPT},
		{"role": "user", "content": topic},
	]

	try:
		resp = openai_client.chat.completions.create(
			model="gpt-4o-mini",
			messages=messages,  # type: ignore
			stream=False,
			temperature=0.7,
		)
		content = resp.choices[0].message.content or ""
		return {
			"message": "completed",
			"data": { "text": content },
			"status": "success",
		}
	except Exception as exc:  # noqa: BLE001
		return {
			"message": str(exc),
			"data": {},
			"status": "error",
		}
