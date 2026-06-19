from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/chat")
async def chat(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)