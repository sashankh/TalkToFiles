from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class ChatHistoryRequest(BaseModel):
    messages: List[Message]
    top_k: int = 5


class FileUploadResponse(BaseModel):
    filename: str
    message: str


class QueryResponse(BaseModel):
    answer: str
    source_documents: List[Dict[str, Any]]


class DocumentListResponse(BaseModel):
    documents: List[Dict[str, Any]]