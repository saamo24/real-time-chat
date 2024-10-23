from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi_jwt_auth import AuthJWT
from .models import Message


app = FastAPI()


connections = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()




    except WebSocketDisconnect:
        del connections[user_id]


async def send_message(sender_id: int, receiver_id: int, content: str):
    # Сохранение сообщения в базе данных
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    # db.add(message) - добавьте код для сохранения в базу данных
    # db.commit()

    # Отправка сообщения получателю, если он подключен
    if receiver_id in connections:
        await connections[receiver_id].send_text(f"{sender_id}: {content}")


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            
            
            # Предполагаем, что формат сообщения: "receiver_id:message"




            receiver_id, content = data.split(":", 1)
            await send_message(user_id, int(receiver_id), content)
    except WebSocketDisconnect:
        del connections[user_id]
