from fastapi import APIRouter
from app.api.v1.endpoints import rooms, qa, chat # Import chat

router = APIRouter()
router.include_router(rooms.router, tags=["rooms"])
router.include_router(qa.router, tags=["QA"])
router.include_router(chat.router, tags=["chat"]) # Include chat router