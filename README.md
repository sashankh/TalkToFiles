<<<<<<< HEAD
# TalkToFiles
=======
# TalkToFiles

A document QA system that lets you query and chat with your PDF and text files.

## Features

- File monitoring for automatic processing of new files
- Support for PDF and TXT files
- Azure OpenAI integration for embeddings and LLM responses
- Local vector storage using Qdrant
- REST API for programmatic access
- Web-based chat interface
- Search across your documents with natural language queries

## Prerequisites

- Python 3.8+
- Azure OpenAI API access (with embeddings and GPT-4o models)
- Windows PowerShell (for setup.ps1)

## Setup

1. Clone this repository
2. Create a `.env` file with the following variables:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-large
AZURE_OPENAI_COMPLETION_DEPLOYMENT=gpt-4o
WATCH_DIRECTORY=C:/Users/YourName/Documents/TalkToFiles
```

3. Run the setup script to create a virtual environment and install dependencies:

```
.\setup.ps1
```

## Running the Application

You can run the application using the setup script:

```
.\setup.ps1 -run
```

Or manually:

```
# Activate the virtual environment
.\.venv\Scripts\activate

# Run the app
python -m src.main
```

## API Endpoints

- `POST /api/query`: Query documents with a question
  - Request: `{"query": "What is...", "top_k": 5}`
  - Response: `{"answer": "...", "source_documents": [...]}`

- `POST /api/chat`: Chat with history
  - Request: `{"messages": [{"role": "user", "content": "..."}], "top_k": 5}`
  - Response: `{"answer": "...", "source_documents": [...]}`

## Web Interface

Open your browser and navigate to:
```
http://localhost:8001
```

## Adding Documents

Place your PDF or TXT files in the configured `WATCH_DIRECTORY`. The application will automatically process new files and make them available for querying.
>>>>>>> 0aabad8 (initial commit)
