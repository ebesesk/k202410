# websocket 중계서버
import asyncio
import websockets
import json
from run_websockets import get_access_token

async def relay(ws_from, ws_to):
    async for message in ws_from:
        print(f"Relaying message: {message}")
        await ws_to.send(message)

async def handler(websocket, path):
    url = "wss://openapi.ls-sec.co.kr:9443/websocket"
    data = {
        "header":{"token":'', "tr_type":"3"}, 
        "body":{"tr_cd": "NWS",  "tr_key": "NWS001"}
        }
    async with websockets.connect(url) as destination:
        res = await websocket.recv()
        print('res: ', res)
        data['header']['token'] = get_access_token(res)
        await destination.send(json.dumps(data))
        while True:
            try:
                await relay(destination, websocket)
            except websockets.exceptions.ConnectionClosedOK as e:
                print('error: ', e)
                break
            except KeyboardInterrupt:
                await websocket.close()
                break

async def start_server():
    server = websockets.serve(handler, "localhost", 876)
    await asyncio.gather(server)
    # await asyncio.get_event_loop().run_until_complete(server)
    # await asyncio.get_event_loop().run_forever()

asyncio.run(start_server())