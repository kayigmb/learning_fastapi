import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy import select
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from database import db
from logger import logger
from models import Room
from typeModels import RoomItems

router = APIRouter(tags=["webrtc"])


class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()

        if room not in self.active_connections:
            self.active_connections[room] = []

        self.active_connections[room].append(websocket)

    async def disconnect(self, websocket: WebSocket, room: str):
        self.active_connections[room].remove(websocket)

        if len(self.active_connections[room]) == 0:
            del self.active_connections[room]

    async def send(self, room: str, message: str):
        if room in self.active_connections:
            for rooms in self.active_connections[room]:
                await rooms.send_text(f"{message}")


manager = ConnectionManager()


@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str, database: db):
    try:
        await manager.connect(websocket, room)

        await manager.send(room, json.dumps({"type": "join"}))

        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                match message["type"]:
                    case "offer":
                        await manager.send(
                            room,
                            json.dumps({"type": "offer", "offer": message["offer"]}),
                        )
                    case "answer":
                        await manager.send(
                            room,
                            json.dumps({"type": "answer", "answer": message["answer"]}),
                        )
                    case "ice-candidate":
                        await manager.send(
                            room,
                            json.dumps(
                                {
                                    "type": "ice-candidate",
                                    "candidate": message["candidate"],
                                }
                            ),
                        )
                    case "message":
                        await manager.send(room, message["message"])
            except WebSocketDisconnect:
                await manager.disconnect(websocket, room)
                break

    except Exception:
        logger.info("Error in the socket")
        await manager.disconnect(websocket, room)


@router.post("/ws")
async def socketRoomCreator(room: RoomItems, database: db):
    try:
        getRoom = select(Room).where(Room.roomName == room.roomName)
        result = database.execute(getRoom)
        isRoomExist = result.scalars().first()
        if isRoomExist:
            return JSONResponse(
                content={"message": "Room name already exist"},
                status_code=HTTP_406_NOT_ACCEPTABLE,
            )
        saveNewRoom = Room(
            roomName=room.roomName, channelConnection=room.roomConnection
        )
        database.save(saveNewRoom)
        database.commit()
        logger.info(f"Room Created {room.roomName}")
        return JSONResponse(
            content={"message": "Room has been Created  succesfully"},
            status_code=HTTP_201_CREATED,
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            content={"message": "Internal Server Error"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
