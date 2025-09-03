from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.init_db import get_db
from app.core.dependencies import get_mongo_db
from app.services import room_service, chat_service, vector_service
from app.schemas.chat import ChatRoomResponse
from typing import List

router = APIRouter()

@router.get("/users/{user_id}/rooms", response_model=List[ChatRoomResponse])
async def read_user_rooms(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    rooms = await room_service.get_rooms_by_user_id(db, user_id)
    if not rooms:
        raise HTTPException(status_code=404, detail="No rooms found for this user")
    return rooms

@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_and_contents(
    room_id: int,
    db_mysql: AsyncSession = Depends(get_db),
    db_mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Deletes a room and all its associated data:
    1. Vectors from Pinecone
    2. Chat messages from MongoDB
    3. The room record from MySQL
    """
    try:
        # 1. Delete vectors from Pinecone
        vector_service.delete_vectors_by_room_id(str(room_id))

        # 2. Delete chat messages from MongoDB
        await chat_service.delete_chat_messages_by_room_id(db_mongo, room_id)

        # 3. Delete the room from MySQL
        await room_service.delete_rooms_by_user_id(db_mysql, room_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error deleting room {room_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete room and its contents: {e}")
