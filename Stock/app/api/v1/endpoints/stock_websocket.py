from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Request, Header
from sqlalchemy.orm import Session  # 상단에 추가
import json
from app.utils.dependencies import get_db, verify_token, get_current_user
from app.websockets.handlers import handle_websocket

router = APIRouter()

# 웹소켓 서버 테스트########################################################################################


@router.websocket("/ws/{username}/{tr_cd}/{code}")
async def websocket_endpoint(
        websocket: WebSocket,
        username: str,
        tr_cd: str,
        code: str
    ):
    try:
        await websocket.accept()
        authenticated = False
        
        # 초기 인증 메시지 대기
        try:
            data = await websocket.receive_json()
            if data.get('type') == 'auth':
                token = data.get('token')
                print('token:', token)
                user = await verify_token(token) # verify_token 함수는 사용자 정보를 반환하거나 예외를 발생시킴
                
                if user:
                        await websocket.send_json({
                            'type': 'auth_response',
                            'status': 'success'
                        })
                        print(f"User {username} authenticated")
                        # 인증 성공 시 실제 웹소켓 핸들러 호출
                        await handle_websocket(websocket, username, tr_cd, code)
                else:
                    await websocket.send_json({
                        'type': 'auth_response',
                        'status': 'error',
                        'message': 'Invalid token'
                    })
            else:
                await websocket.send_json({
                    'type': 'auth_response',
                    'status': 'error',
                    'message': 'Authentication required'
                })
                
        except json.JSONDecodeError:
            await websocket.send_json({
                'type': 'error',
                'message': 'Invalid message format'
            })
            
    except WebSocketDisconnect:
        print(f"Client {username} disconnected")
    except Exception as e:
        print(f"WebSocket 연결 오류: {str(e)}")
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get("/test_ws-info")
async def get_test_websocket_info(
        request: Request,
        tr_cd: str,
        code: str,
        key: str = Header(None, alias="X-API-KEY"),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    """WebSocket 연결 정보를 반환하는 엔드포인트"""
    # print('get_test_websocket_info:', tr_cd, code, key)
    try:
        username = current_user.get('username')
        ws_url = f"/stock/ws/{username}/{tr_cd}/{code}"
        # print('get_test_websocket_info:', ws_url)
        return {
            "status": "success",
            "websocket_url": ws_url,
            "username": username,
            "tr_cd": tr_cd,
            "code": code
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
        