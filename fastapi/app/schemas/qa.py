
from pydantic import BaseModel

class UpsertRequest(BaseModel):
    title: str

class QueryRequest(BaseModel):
    title: str
    question: str

class UpsertResponse(BaseModel):
    message: str
    base_id: str
    chunk_count: int

class QueryResponse(BaseModel):
    answer: str
    source_document_id: str
