from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class ChatRequest(BaseModel):
    chatroom_title: str
    message: str

class ChatMessage(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id") # Make it truly optional with a default
    room_id: int
    sequence_number: int
    sender: str # "user" or "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "room_id": 123,
                "sequence_number": 1,
                "sender": "user",
                "content": "Hello, how are you?",
                "timestamp": "2023-10-27T10:00:00Z"
            }
        },
        arbitrary_types_allowed=True, # Allow ObjectId
        extra='ignore' # Ignore extra fields when loading from dict
    )

class ChatRoomResponse(BaseModel):
    room_id: int
    title: str

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "room_id": 1,
                "title": "My First Chat Room"
            }
        }
    )