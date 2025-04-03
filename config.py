import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")

# Model names
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-large")
AZURE_OPENAI_COMPLETION_DEPLOYMENT = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT", "gpt-4o")

# File watching configuration
WATCH_DIRECTORY = os.getenv("WATCH_DIRECTORY", str(Path(__file__).parent / "Documents"))
# Directory creation moved to main.py where it belongs

# Qdrant configuration
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
VECTOR_SIZE = 3072  # Size for text-embedding-3-large (updated from 1536)

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))