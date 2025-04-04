from typing import List, Dict, Any
from src.embeddings.azure_openai import AzureOpenAIClient


class DocumentQueryModel:
    def __init__(self):
        """Initialize the document query model"""
        self.client = AzureOpenAIClient()
    
    def query(self, query: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """
        Query the document model with the user query and relevant documents
        
        Args:
            query: User's question
            relevant_docs: List of relevant document chunks retrieved from search
            
        Returns:
            Generated response from the model
        """
        # Construct system prompt
        system_prompt = """You are a helpful assistant that answers questions based on the provided document context.
        - Answer only based on the context provided
        - If you don't know the answer or the context doesn't contain relevant information, say so
        - Include relevant source information in your response
        - Be concise and accurate
        """
        
        # Format the context from relevant documents
        context = self._format_context(relevant_docs)
        
        # Construct user prompt with query and context
        user_prompt = f"""Question: {query}
        
        Context:
        {context}
        
        Please answer the question based on the provided context:"""
        
        # Get completion from the model
        response = self.client.get_completion(system_prompt, user_prompt)
        return response
    
    def _format_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Format the relevant documents into a text context for the model"""
        context_parts = []
        
        for i, doc in enumerate(relevant_docs):
            metadata = doc["metadata"]
            source = metadata.get("source", "Unknown")
            
            context_parts.append(f"Document {i+1} [Source: {source}]:")
            context_parts.append(doc["text"])
            context_parts.append("")  # Empty line for separation
            
        return "\n".join(context_parts)