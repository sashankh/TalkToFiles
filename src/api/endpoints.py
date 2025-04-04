from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Optional, List
import os
import shutil
from pathlib import Path

from api.models import (
    QueryRequest, QueryResponse, ChatHistoryRequest, 
    FileUploadResponse, DocumentListResponse
)
from embeddings.azure_openai import AzureOpenAIClient
from database.qdrant_client import QdrantDB
from models.gpt4 import DocumentQueryModel
from file_processing.document_processor import process_document
from config import WATCH_DIRECTORY

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


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: QdrantDB = Depends(get_qdrant_db),
    openai_client: AzureOpenAIClient = Depends(get_openai_client)
):
    """
    Upload a file and process it
    """
    try:
        # Print debug information
        print(f"Upload requested for file: {file.filename}")
        print(f"WATCH_DIRECTORY path: {WATCH_DIRECTORY}")
        
        # Ensure WATCH_DIRECTORY is an absolute path
        abs_watch_dir = os.path.abspath(WATCH_DIRECTORY)
        print(f"Absolute WATCH_DIRECTORY path: {abs_watch_dir}")
        
        # Create the watch directory if it doesn't exist
        os.makedirs(abs_watch_dir, exist_ok=True)
        print(f"Directory exists or was created: {os.path.exists(abs_watch_dir)}")
        
        # Save the file to the watch directory with absolute path
        file_path = os.path.join(abs_watch_dir, file.filename)
        print(f"Saving file to: {file_path}")
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"File saved successfully to: {file_path}")
        except Exception as save_error:
            print(f"Error saving file: {save_error}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(save_error)}")
        
        # Process the document using the same logic as in main.py
        print(f"Processing document: {file_path}")
        document_chunks = process_document(file_path)
        print(f"Document processed, chunks extracted: {len(document_chunks)}")
        
        if document_chunks:
            # Extract texts and metadata
            texts = [chunk[0] for chunk in document_chunks]
            metadatas = [chunk[1] for chunk in document_chunks]
            
            # Generate embeddings
            print(f"Generating embeddings for {len(texts)} chunks")
            embeddings = openai_client.get_embeddings(texts)
            print(f"Embeddings generated: {len(embeddings)}")
            
            if embeddings:
                # Add texts to database
                print(f"Adding {len(texts)} chunks to database")
                db.add_texts(texts, embeddings, metadatas)
                print(f"Successfully added to database")
                
                return FileUploadResponse(
                    filename=file.filename,
                    message=f"File uploaded and processed successfully. Added {len(texts)} chunks to the database."
                )
            else:
                error_msg = f"Failed to generate embeddings for {file.filename}"
                print(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
        else:
            error_msg = f"No text chunks extracted from {file.filename}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
            
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        print(error_msg)
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/documents", response_model=DocumentListResponse)
async def get_documents(
    db: QdrantDB = Depends(get_qdrant_db)
):
    """
    Get a list of all indexed documents
    """
    documents = db.get_document_list()
    return DocumentListResponse(documents=documents)