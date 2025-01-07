from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # {username: set(codes)}

    async def connect(self, websocket: WebSocket, username: str, code: str):
        await websocket.accept()
        if username not in self.active_connections:
            self.active_connections[username] = {}
            self.subscriptions[username] = set()
        self.active_connections[username][code] = websocket
        self.subscriptions[username].add(code)
        print(f"WebSocket 연결됨: {username}, {code}")

    def disconnect(self, username: str, code: str):
        if username in self.active_connections:
            if code in self.active_connections[username]:
                del self.active_connections[username][code]
            if code in self.subscriptions[username]:
                self.subscriptions[username].remove(code)
            if not self.active_connections[username]:
                del self.active_connections[username]
                del self.subscriptions[username]
            print(f"WebSocket 연결 해제: {username}, {code}")

    async def send_personal_message(self, message: dict, username: str, code: str):
        if username in self.active_connections and code in self.active_connections[username]:
            await self.active_connections[username][code].send_json(message)

    def get_subscriptions(self, username: str) -> Set[str]:
        return self.subscriptions.get(username, set())

    async def broadcast(self, message: dict):
        for username in self.active_connections:
            for code in self.active_connections[username]:
                await self.send_personal_message(message, username, code)