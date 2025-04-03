import os
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_COMPLETION_DEPLOYMENT,
    VECTOR_SIZE
)

# Define the working embedding model
EMBEDDING_MODEL = "text-embedding-3-large"

# Print all configuration values
print("=== Configuration Values ===")
print(f"AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
print(f"AZURE_OPENAI_API_KEY: {'*' * 8 + AZURE_OPENAI_API_KEY[-4:] if AZURE_OPENAI_API_KEY else 'Not set'}")
print(f"AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION}")
print(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
print(f"AZURE_OPENAI_COMPLETION_DEPLOYMENT: {AZURE_OPENAI_COMPLETION_DEPLOYMENT}")
print(f"VECTOR_SIZE: {VECTOR_SIZE}")
print("===========================\n")

# Create the Azure OpenAI client
print("Creating Azure OpenAI client...")
try:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    print("Client created successfully!\n")
except Exception as e:
    print(f"Error creating client: {e}")
    exit(1)

print(f"Testing Azure OpenAI embedding model: {EMBEDDING_MODEL}")
print(f"API version: {AZURE_OPENAI_API_VERSION}")
print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")

try:
    # Generate embeddings for sample phrases
    print("\nGenerating embeddings...")
    sample_texts = ["first phrase", "second phrase", "third phrase"]
    print(f"Sample texts: {sample_texts}")
    
    response = client.embeddings.create(
        input=sample_texts,
        model=EMBEDDING_MODEL
    )

    # Print embedding information
    print("\nEmbedding results:")
    for item in response.data:
        length = len(item.embedding)
        print(
            f"data[{item.index}]: length={length}, "
            f"[{item.embedding[0]:.6f}, {item.embedding[1]:.6f}, "
            f"..., {item.embedding[length-2]:.6f}, {item.embedding[length-1]:.6f}]"
        )
    
    print(f"\nUsage: {response.usage}")
    print("\nEmbed test completed successfully!")

except Exception as e:
    print(f"\nError testing embeddings: {e}")
    print("\nPlease check your Azure OpenAI deployments in the Azure Portal to confirm the correct deployment name.")