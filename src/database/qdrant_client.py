import os
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid
from config import QDRANT_PATH, COLLECTION_NAME, VECTOR_SIZE


class QdrantDB:
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantDB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        """Initialize the Qdrant database client"""
        # Only initialize once
        if self._initialized:
            return
            
        # Ensure the directory exists
        os.makedirs(QDRANT_PATH, exist_ok=True)
        
        # Initialize the client with local persistence
        self.client = QdrantClient(path=QDRANT_PATH)
        self._init_collection()
        self._initialized = True
        
    def _init_collection(self):
        """Initialize the vector collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE
                ),
            )
            
    def add_texts(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]) -> List[str]:
        """
        Add text chunks with embeddings and metadata to the database
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors for each chunk
            metadatas: List of metadata dictionaries for each chunk
            
        Returns:
            List of IDs for the added points
        """
        if len(texts) != len(embeddings) or len(embeddings) != len(metadatas):
            raise ValueError("Length of texts, embeddings, and metadatas must be the same")
        
        # Generate unique IDs for each point
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Create points with payloads
        points = []
        for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
            # Combine text content and metadata
            payload = {
                "text": text,
                **metadata
            }
            
            # Add the point
            points.append(
                models.PointStruct(
                    id=ids[i],
                    vector=embedding,
                    payload=payload
                )
            )
        
        # Insert the points into the collection
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
        return ids
        
    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar texts using the query vector
        
        Args:
            query_vector: The query embedding vector
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing text, metadata, and similarity score
        """
        search_results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit
        )
        
        results = []
        for result in search_results:
            payload = result.payload
            text = payload.pop("text")
            results.append({
                "text": text,
                "metadata": payload,
                "similarity": result.score
            })
            
        return results