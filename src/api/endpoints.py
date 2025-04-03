from fastapi import APIRouter, Depends
from typing import Optional, List

from api.models import QueryRequest, QueryResponse, ChatHistoryRequest
from embeddings.azure_openai import AzureOpenAIClient
from database.qdrant_client import QdrantDB
from models.gpt4 import DocumentQueryModel

# Create router
router = APIRouter()

# Dependency for OpenAI client
def get_openai_client():
    return AzureOpenAIClient()

# Dependency for Qdrant DB
def get_qdrant_db():
    return QdrantDB()

# Dependency for Query Model
def get_query_model():
    return DocumentQueryModel()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    openai_client: AzureOpenAIClient = Depends(get_openai_client),
    db: QdrantDB = Depends(get_qdrant_db),
    query_model: DocumentQueryModel = Depends(get_query_model)
):
    """
    Query documents with a natural language question
    """
    # Generate embedding for the query
    query_embedding = openai_client.get_embeddings([request.query])[0]
    
    # Search for relevant documents
    search_results = db.search(query_embedding, limit=request.top_k)
    
    # If no relevant documents found
    if not search_results:
        return QueryResponse(
            answer="No relevant documents found in the database. Try adding documents first.",
            source_documents=[]
        )
    
    # Query the model with retrieved documents
    answer = query_model.query(request.query, search_results)
    
    # Format source documents for response
    formatted_sources = []
    for doc in search_results:
        formatted_sources.append({
            "text": doc["text"],
            "source": doc["metadata"].get("source", "Unknown"),
            "similarity": doc["similarity"]
        })
    
    return QueryResponse(
        answer=answer,
        source_documents=formatted_sources
    )


@router.post("/chat", response_model=QueryResponse)
async def chat_with_documents(
    request: ChatHistoryRequest,
    openai_client: AzureOpenAIClient = Depends(get_openai_client),
    db: QdrantDB = Depends(get_qdrant_db),
    query_model: DocumentQueryModel = Depends(get_query_model)
):
    """
    Chat with documents with history
    """
    # Get the last user message as query
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        return QueryResponse(
            answer="No user message found in the request.",
            source_documents=[]
        )
    
    last_user_message = user_messages[-1].content
    
    # Generate embedding for the query
    query_embedding = openai_client.get_embeddings([last_user_message])[0]
    
    # Search for relevant documents
    search_results = db.search(query_embedding, limit=request.top_k)
    
    # If no relevant documents found
    if not search_results:
        return QueryResponse(
            answer="No relevant documents found in the database. Try adding documents first.",
            source_documents=[]
        )
    
    # Query the model with retrieved documents
    answer = query_model.query(last_user_message, search_results)
    
    # Format source documents for response
    formatted_sources = []
    for doc in search_results:
        formatted_sources.append({
            "text": doc["text"],
            "source": doc["metadata"].get("source", "Unknown"),
            "similarity": doc["similarity"]
        })
    
    return QueryResponse(
        answer=answer,
        source_documents=formatted_sources
    )