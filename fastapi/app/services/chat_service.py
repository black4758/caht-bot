from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.chat import ChatMessage
from app.core.dependencies import get_mongo_db
from fastapi import Depends

async def get_next_sequence_number(db: AsyncIOMotorDatabase, room_id: int) -> int:
    last_message = await db["chat_messages"].find_one(
        {"room_id": room_id},
        sort=[("sequence_number", -1)]
    )
    if last_message:
        return last_message["sequence_number"] + 1
    return 1

async def create_chat_message(
    db: AsyncIOMotorDatabase,
    room_id: int,
    sender: str,
    content: str
) -> ChatMessage:
    sequence_number = await get_next_sequence_number(db, room_id)
    chat_message = ChatMessage(
        id=None, # Explicitly set to None
        room_id=room_id,
        sequence_number=sequence_number,
        sender=sender,
        content=content
    )
    message_data_to_insert = chat_message.model_dump(by_alias=True, exclude={'id'})
    result = await db["chat_messages"].insert_one(message_data_to_insert)
    chat_message.id = str(result.inserted_id)
    return chat_message

async def get_chat_messages(db: AsyncIOMotorDatabase, room_id: int) -> list[ChatMessage]:
    messages = []
    async for message in db["chat_messages"].find({"room_id": room_id}).sort("sequence_number", 1):
        if "_id" in message:
            message["_id"] = str(message["_id"])
        messages.append(ChatMessage(**message))
    return messages

async def delete_chat_messages_by_room_id(db: AsyncIOMotorDatabase,room_id: int) :
    await db["chat_messages"].delete_many({"room_id": room_id})