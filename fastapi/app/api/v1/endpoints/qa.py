import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase # Import for MongoDB dependency
from sqlalchemy.ext.asyncio import AsyncSession # Import for SQLAlchemy session

from app.services import pdf_service, vector_service, chat_service # Import chat_service
from app.schemas.qa import UpsertResponse, QueryResponse
from app.core.dependencies import get_mongo_db # Import get_mongo_db
from app.db.init_db import get_db, Room # Import MySQL dependencies

router = APIRouter()

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upsert-pdf/", response_model=UpsertResponse)
async def upsert_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    user_id: int = Form(...), # New argument
    db_mysql: AsyncSession = Depends(get_db) # MySQL DB session
):
    """
    PDF 파일에서 직접 텍스트를 추출하고, 조각으로 나눈 후 임베딩하여 Pinecone에 저장합니다.
    추출된 텍스트는 파일로 캐싱하여 재사용합니다.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # 1. Save PDF file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Insert into rooms table
        new_room = Room(user_id=user_id, title=title, file_path=file_location)
        db_mysql.add(new_room)
        await db_mysql.commit()
        await db_mysql.refresh(new_room)
        room_id = new_room.id

        # 3. Process PDF text and upsert to Pinecone
        await file.seek(0)
        text = await pdf_service.get_text_from_pdf(title, file) # title is still used for PDF processing
        # Use room_id as the base_id for Pinecone
        chunk_count = vector_service.upsert_text_to_pinecone(room_id=str(room_id), text=text)

        return {
            "message": f"Successfully split into {chunk_count} chunks, embedded, and stored!",
            "base_id": str(room_id), # Return room_id as base_id
            "chunk_count": chunk_count
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        await db_mysql.rollback() # Rollback in case of error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/query-pdf/", response_model=QueryResponse)
async def query_pdf(
    room_id: int = Form(...),
    question: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db) # Add MongoDB dependency
):
    """
    특정 PDF(room_id)에 대해 질문(question)하고 Gemini를 통해 답변을 받습니다.
    """
    try:
        # Save user's question to MongoDB
        await chat_service.create_chat_message(
            db=db,
            room_id=room_id,
            sender="user",
            content=question
        )

        answer = vector_service.query_from_pinecone(room_id=str(room_id), question=question)

        await chat_service.create_chat_message(
            db=db,
            room_id=room_id,
            sender="system",
            content=answer
        )

        return {"answer": answer, "source_document_id": str(room_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during query: {str(e)}")
