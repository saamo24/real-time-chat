# from fastapi import FastAPI, Depends
# from .auth import auth_router
# from .db import Base, engine
# from fastapi_jwt_auth import AuthJWT

# app = FastAPI()

# Base.metadata.create_all(bind=engine)

# @app.get("/hello")
# def hello(Authorize: AuthJWT = Depends()):

#     try:
#         # Require JWT token
#         Authorize.jwt_required()
#         current_user = Authorize.get_jwt_subject()
#         return {"message": f"Hello {current_user}!"}
#     except Exception as e:
#         return {"detail": str(e)}, 401
    

# app.include_router(auth_router, prefix="/api")


from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect
from fastapi_jwt_auth import AuthJWT
from .auth import auth_router
from .db import Base, engine
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get('/')
async def get():
    return HTMLResponse(html)


# Base.metadata.create_all(bind=engine)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Test</title>
</head>
<body>
    <div class="container mt-3">
    <h1>WebSocket chat test</h1>
    <h2>ID: <span id="ws-id"></span></h2>
    <form action="" onsubmit="sendMessage(event)">
        <input type="text" class="form-control" id="messageText" autocomplete="off"/>
        <button class="btn btn-outline-primary mt-2">send</button>
    </form>
    <ul id="messages" class="mt-5">
    </ul>

    </div>

        <script>

            var clinet_id = Date.now()
            document.querySelector("#ws-id").textContent = clinet_id
            
            var ws = new WebSocket(`ws://127.0.0.1:8000/ws/${client_id}/`);
            ws.onmessage = function(event){
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)            
            };

            function sendMessage(event) {
                var input = document.getElementById('messageText')
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }

        </script>
</body>
</html>


"""


class ConnectionManager():
    def __init__(self):
        self.active_connections:  list[WebSocket] = []


        async def connect(self, websocet: WebSocket):
            await websocet.accept()
            self.acive_connections.append(websocet)

        def disconnect(self, websocet: WebSocket):
            self.active_connections.remove(websocet)
        
        async def send_personal_message(self, message: str, websocet: WebSocket):

            await websocet.send_text(message)

        async def brodcast(self, message: str):
            for con in self.active_connections:
                await con.end_text(message)

manager = ConnectionManager()


@app.websocket("/ws/{client_id}/")
async def chat(websocket: WebSocket, clinet_id: int): # Authorize: AuthJWT = Depends()
    # Accept the WebSocket connection
    # await websocket.accept()

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"you -> {data}", websocket)
            await manager.brodcast(f'brodcast client({clinet_id}) -> {data}', websocket)
    except WebSocketDisconnect:
        manager.disconnect()
        await manager.brodcast(f"client #{clinet_id} lqum e xaxy")


    
    # Extract the JWT token from query parameters (or headers)
    # token = websocket.query_params.get("token")
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(f'message {data}')
    #     print(data)
    # try:
    #     # Validate the token
    #     # Authorize.jwt_required(token=token)

    #     # Get the current user from the token
    #     # current_user = Authorize.get_jwt_subject() {current_user}
    #     await websocket.send_text(f"Hello ! You are now connected to the chat.")

    #     while True:
    #         data = await websocket.receive_text()
    #         await websocket.send_text(f"Message received: {data}")

    # except WebSocketDisconnect:
    #     print("Client disconnected")
    # except Exception as e:
    #     await websocket.send_text(f"Error: {str(e)}")

# Include the authentication router
app.include_router(auth_router, prefix="/api")

@app.get("/hello")
def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        return {"message": f"Hello {current_user}!"}
    except Exception as e:
        return {"detail": str(e)}, 401
