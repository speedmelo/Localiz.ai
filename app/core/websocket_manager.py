# app/core/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # room -> list of ws

    async def connect(self, websocket: WebSocket, room: str = "general"):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str = "general"):
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)

    async def send_to_room(self, message: dict, room: str):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Remove conexão morta
                    await self.disconnect(connection, room)