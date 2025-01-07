from .connection import ConnectionManager
from typing import Dict
import asyncio
import json
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.running_tasks: Dict[str, asyncio.Task] = {}

    async def start_realtime_data(self, username: str, code: str):
        task_key = f"{username}_{code}"
        if task_key not in self.running_tasks:
            self.running_tasks[task_key] = asyncio.create_task(
                self._send_realtime_data(username, code)
            )

    async def stop_realtime_data(self, username: str, code: str):
        task_key = f"{username}_{code}"
        if task_key in self.running_tasks:
            self.running_tasks[task_key].cancel()
            del self.running_tasks[task_key]

    async def _send_realtime_data(self, username: str, code: str):
        try:
            while True:
                # 실시간 데이터 생성 또는 조회
                real_data = {
                    "type": "real",
                    "code": code,
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "현재가": 0,
                        "거래량": 0,
                        # ... 기타 실시간 데이터
                    }
                }
                
                await self.connection_manager.send_personal_message(
                    real_data, username, code
                )
                await asyncio.sleep(1)  # 1초 대기
                
        except asyncio.CancelledError:
            print(f"실시간 데이터 전송 중단: {username}, {code}")
        except Exception as e:
            print(f"실시간 데이터 전송 오류: {str(e)}")