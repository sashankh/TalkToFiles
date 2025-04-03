from typing import List
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_COMPLETION_DEPLOYMENT
)

# Use the working embedding model
EMBEDDING_MODEL = "text-embedding-3-large"

class AzureOpenAIClient:
    def __init__(self):
        """Initialize the Azure OpenAI client"""
        # Use the dedicated AzureOpenAI client
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Azure OpenAI
        
        Args:
            texts: List of text strings to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        try:
            # Process texts in batches to avoid exceeding token limits
            embeddings = []
            batch_size = 10
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                response = self.client.embeddings.create(
                    input=batch_texts,
                    model=EMBEDDING_MODEL  # Using the working model directly
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
            
    def get_completion(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate completion using Azure OpenAI GPT-4o
        
        Args:
            system_prompt: System instructions
            user_prompt: User query with context
            
        Returns:
            Generated completion text
        """
        try:
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_COMPLETION_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                top_p=0.95,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating completion: {e}")
            return f"Error: {str(e)}"