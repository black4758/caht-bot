
import os
import fitz  # PyMuPDF
from fastapi import UploadFile, HTTPException
from app.core.config import TEXT_CACHE_DIR

os.makedirs(TEXT_CACHE_DIR, exist_ok=True)

async def get_text_from_pdf(title: str, file: UploadFile) -> str:
    text_file_path = os.path.join(TEXT_CACHE_DIR, f"{title}.txt")

    if os.path.exists(text_file_path):
        print(f"Loading text from cache: {text_file_path}")
        with open(text_file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print("No cache found. Extracting text directly from PDF with PyMuPDF...")
        try:
            pdf_content = await file.read()
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            
            text = " ".join(text_parts)
            doc.close()

            print(f"Saving text to cache: {text_file_path}")
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {e}")
