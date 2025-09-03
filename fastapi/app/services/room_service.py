from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from app.schemas.chat import ChatRoomResponse
from app.db.init_db import Room

async def get_rooms_by_user_id(db: AsyncSession, user_id: int) -> list[ChatRoomResponse]:
    result = await db.execute(select(Room).filter(Room.user_id == user_id))
    rooms = result.scalars().all()
    return [ChatRoomResponse(room_id=room.id, title=room.title) for room in rooms]

async def delete_rooms_by_user_id(db: AsyncSession, room_id: int):
    stmt = delete(Room).where(Room.id == room_id)
    await db.execute(stmt)
    await db.commit()