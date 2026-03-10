# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from typing import List

# router = APIRouter(prefix="/ws", tags=["WebSocket"])

# send_connections: List[WebSocket] = []
# receive_connections: List[WebSocket] = []

# @router.websocket("/connect/send")
# async def websocket_endpoint_send(websocket: WebSocket):
#     await websocket.accept()
#     send_connections.append(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()  # Aguarda uma mensagem do cliente
#             message = {"type": "broadcast", "data": data}
#             for connection in receive_connections:
#                 await connection.send_text(message["data"])
#     except WebSocketDisconnect:
#         send_connections.remove(websocket)
#         print("Client disconnected from /connect/send")

# @router.websocket("/connect/receive")
# async def websocket_endpoint_receive(websocket: WebSocket):
#     await websocket.accept()
#     receive_connections.append(websocket)
#     try:
#         while True:
#             await websocket.receive_text()  # Mantenha a conexão ativa
#     except WebSocketDisconnect:
#         receive_connections.remove(websocket)
#         print("Client disconnected from /connect/receive")


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from typing import List, Dict


router = APIRouter(prefix="/ws", tags=["WebSocket"])
rooms: Dict[str, List[WebSocket]] = {}


@router.websocket("/connect/send/{room_name}")
async def websocket_endpoint_send(websocket: WebSocket, room_name: str):
    await websocket.accept()
    if room_name not in rooms:
        rooms[room_name] = []
    rooms[room_name].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = {"type": "broadcast", "data": data}
            for connection in rooms[room_name]:
                if connection != websocket:  # Não envie a mensagem de volta para o remetente
                    await connection.send_text(message["data"])
    except WebSocketDisconnect:
        rooms[room_name].remove(websocket)
        if not rooms[room_name]:
            del rooms[room_name]
        print(f"Client disconnected from /connect/send/{room_name}")


@router.websocket("/connect/receive/{room_name}")
async def websocket_endpoint_receive(websocket: WebSocket, room_name: str):
    await websocket.accept()
    if room_name not in rooms:
        rooms[room_name] = []
    rooms[room_name].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        rooms[room_name].remove(websocket)
        if not rooms[room_name]:
            del rooms[room_name]
        print(f"Client disconnected from /connect/receive/{room_name}")


@router.get(
    "/rooms",
    tags=["WebSocket"],
    summary="List websocket rooms",
    description="Return the list of currently active rooms.",
    response_description="List of active rooms.",
)
async def get_all_rooms():
    """
    Returns a list of all currently active rooms.
    """
    return {"rooms": list(rooms.keys())}

        


