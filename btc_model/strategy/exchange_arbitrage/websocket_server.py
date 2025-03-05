from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import List

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/price_diff")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 这里获取您的策略数据
            price_data = {
                "price_data": [
                    {
                        "symbol": "BTC/USDT",
                        "exchange_a_price": strategy.get_exchange_a_price(),
                        "exchange_b_price": strategy.get_exchange_b_price(),
                        "price_diff": strategy.get_price_diff(),
                        "diff_percentage": strategy.get_diff_percentage()
                    }
                ]
            }
            await websocket.send_text(json.dumps(price_data))
            await asyncio.sleep(1)  # 每秒更新一次
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket) 