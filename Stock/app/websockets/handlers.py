from fastapi import WebSocket, WebSocketDisconnect
from .manager import WebSocketManager
import json
import asyncio
from pathlib import Path

websocket_manager = WebSocketManager()

# async def handle_websocket(
#     websocket: WebSocket,
#     username: str,
#     code: str
# ):
#     try:
#         await websocket_manager.connection_manager.connect(websocket, username, code)
#         await websocket_manager.start_realtime_data(username, code)

#         try:
#             while True:
#                 data = await websocket.receive_text()
#                 message = json.loads(data)
                
#                 # 클라이언트 메시지 처리
#                 if message.get("type") == "subscribe":
#                     print(f"구독 요청: {username}, {code}")
#                 elif message.get("type") == "unsubscribe":
#                     print(f"구독 해제 요청: {username}, {code}")
                    
#         except WebSocketDisconnect:
#             print(f"WebSocket 연결 해제: {username}, {code}")
#         finally:
#             await websocket_manager.stop_realtime_data(username, code)
#             websocket_manager.connection_manager.disconnect(username, code)
            
#     except Exception as e:
#         print(f"WebSocket 처리 오류: {str(e)}")
        


# 웹소켓 서버 테스트########################################################################################
async def send_stock_data(websocket, username: str, tr_cd: str, code: str):
    file_path = Path("app/utils/websocket_response.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            while True:  # 무한 루프로 파일 반복 읽기
                f.seek(0)  # 파일 포인터를 처음으로 되돌림
                for line in f:
                    try:
                        data = json.loads(line)
                        # 요청한 tr_cd와 종목 코드의 데이터만 전송
                        if data["header"]["tr_cd"] == tr_cd and data["header"]["tr_key"] == code:
                            print(f"전송 데이터: {data}")
                            await websocket.send_json(data)
                            await asyncio.sleep(0.3)  # 1초 간격으로 전송
                        else:
                            print(f"전송 데이터: {data}")
                            await websocket.send_json(data)
                            await asyncio.sleep(0.3)  # 1초 간격으로 전송
                    except json.JSONDecodeError:
                        continue  # 잘못된 JSON 라인은 건너뜀
                    
    except Exception as e:
        print(f"데이터 전송 오류: {str(e)}")
        raise

async def handle_websocket(websocket, username: str, tr_cd: str, code: str):
    try:
        # websocket.accept() 제거 - 이미 accept된 상태
        await send_stock_data(websocket, username, tr_cd, code)
        
    except Exception as e:
        print(f"WebSocket 처리 오류: {str(e)}")
        
        
        
        
        