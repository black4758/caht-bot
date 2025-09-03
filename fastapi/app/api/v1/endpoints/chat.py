from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.chat import ChatMessage
from app.services.chat_service import get_chat_messages
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.dependencies import get_mongo_db

router = APIRouter()

@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessage])
async def read_chat_messages(
    room_id: int,
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    messages = await get_chat_messages(db, room_id)
    return messages
