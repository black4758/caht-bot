
from fastapi import FastAPI
from app.api.v1.api import router as api_router # Import the main API router
from app.db.init_db import init_db
from app.core.config import API_V1_STR

app = FastAPI(title="PDF Q&A API with PyMuPDF and Gemini")

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(api_router, prefix=API_V1_STR) # Include the main API router

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF Q&A API with PyMuPDF and Gemini"}
