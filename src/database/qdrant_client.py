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
        try:
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
        except ValueError as e:
            # Handle shape mismatch errors that can occur after adding new documents
            print(f"Error in vector search: {e}")
            print("Attempting to recreate the collection...")
            
            try:
                # Delete and recreate the collection
                if COLLECTION_NAME in [c.name for c in self.client.get_collections().collections]:
                    self.client.delete_collection(collection_name=COLLECTION_NAME)
                    print(f"Collection {COLLECTION_NAME} was deleted")
                
                # Recreate collection
                self._init_collection()
                print(f"Collection {COLLECTION_NAME} was recreated successfully")
                
                # Return empty results since we've reset the collection
                return []
            except Exception as recreate_error:
                print(f"Failed to recreate collection: {recreate_error}")
                return []
        except Exception as e:
            print(f"Unexpected error during search: {e}")
            return []
            
    def get_document_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all unique documents in the database
        
        Returns:
            List of dictionaries containing document information
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if COLLECTION_NAME not in collection_names:
                print(f"Collection {COLLECTION_NAME} does not exist")
                return []
                
            # Count documents to check if database is empty
            count = self.client.count(collection_name=COLLECTION_NAME).count
            if count == 0:
                print("Database is empty, no documents to list")
                return []
                
            print(f"Found {count} points in the database")
            
            # Dictionary to track unique documents by their file path
            unique_docs = {}
            
            # Track which files we've already reported as found
            reported_files = set()
            
            # Scroll through all points in batches
            offset = None
            batch_size = 100
            
            while True:
                response = self.client.scroll(
                    collection_name=COLLECTION_NAME,
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                points = response[0]
                if not points:
                    break
                    
                print(f"Processing {len(points)} points from database")
                
                for point in points:
                    if not point.payload:
                        continue
                    
                    # Extract document identifying information - we need title, source path, and ignore chunk_id
                    source_path = point.payload.get('source', '')
                    title = point.payload.get('title', '')
                    
                    if not source_path:
                        continue
                        
                    # Clean up the path for better matching
                    # Remove any path variations for the same file
                    normalized_path = os.path.normpath(source_path).replace('\\', '/')
                    base_filename = os.path.basename(normalized_path)
                    
                    # Use the normalized path as the key to identify unique documents
                    # This way all chunks from the same document will map to the same key
                    doc_key = normalized_path
                    
                    # If we haven't seen this document yet, add it to our unique docs
                    if doc_key not in unique_docs:
                        # Get additional document metadata
                        file_type = point.payload.get('file_type', '')
                        timestamp = point.payload.get('timestamp', '')
                        
                        # If no title, use filename
                        if not title:
                            title = base_filename
                            
                        # Create a document record with the first chunk we find
                        unique_docs[doc_key] = {
                            'source': normalized_path,
                            'title': title,
                            'file_type': file_type,
                            'timestamp': timestamp
                        }
                        
                        # Only print the "found" message once per file
                        if normalized_path not in reported_files:
                            print(f"Found document: {title} at {normalized_path}")
                            reported_files.add(normalized_path)
                
                # Update offset for next batch
                offset = response[1]
                if offset is None:
                    break
            
            # Convert the dictionary of unique documents to a list
            documents = list(unique_docs.values())
            
            # Sort documents by title for consistent display
            documents.sort(key=lambda x: x['title'].lower())
            
            print(f"Found {len(documents)} unique documents")
            for doc in documents:
                print(f"Final document list: {doc['title']} ({doc['source']})")
            
            return documents
            
        except Exception as e:
            print(f"Error getting document list: {e}")
            import traceback
            traceback.print_exc()
            return []