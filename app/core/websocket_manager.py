# app/core/websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging

from app.core.logging import get_logger

logger = get_logger("websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}   # room -> list of connections
        self.user_connections: Dict[str, WebSocket] = {}           # user_id -> websocket

    async def connect(self, websocket: WebSocket, room: str = "general", user_id: str | None = None):
        await websocket.accept()
        
        if room not in self.active_connections:
            self.active_connections[room] = []
        
        self.active_connections[room].append(websocket)
        
        if user_id:
            self.user_connections[user_id] = websocket

        logger.info(f"WebSocket conectado | Room: {room} | Usuários online: {len(self.get_all_connections())}")

    def disconnect(self, websocket: WebSocket, room: str = "general", user_id: str | None = None):
        try:
            if room in self.active_connections and websocket in self.active_connections[room]:
                self.active_connections[room].remove(websocket)
            
            if not self.active_connections.get(room):
                self.active_connections.pop(room, None)

            if user_id and user_id in self.user_connections:
                del self.user_connections[user_id]
        except Exception as e:
            logger.warning(f"Erro ao desconectar WebSocket: {e}")

    async def send_to_room(self, message: dict, room: str = "general"):
        if room not in self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections[room]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead, room)

    def get_all_connections(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())


# Instância global (importante!)
manager = ConnectionManager()