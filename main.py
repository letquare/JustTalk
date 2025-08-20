import json
from typing import Dict

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()
connections: Dict[str, WebSocket] = {}

@app.get("/")
async def index():
    # отдадим статическую страницу из файла
    return HTMLResponse(open("index.html", "r", encoding="utf-8").read())

@app.websocket("/ws/{user_id}")
async def ws_endpoint(ws: WebSocket, user_id: str):
    await ws.accept()
    connections[user_id] = ws
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue

            to = msg.get("to")
            if not to:
                continue

            payload = {
                "from": user_id,
                "type": msg.get("type"),
                "data": msg.get("data"),
            }

            target = connections.get(to)
            if target:
                await target.send_text(json.dumps(payload))
    except WebSocketDisconnect:
        pass
    finally:
        connections.pop(user_id, None)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=433)
