import os
import sys
import time
import threading
import uvicorn
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.endpoints import router as api_router
from database.qdrant_client import QdrantDB
from embeddings.azure_openai import AzureOpenAIClient
from file_processing.document_processor import process_document
from config import API_HOST, API_PORT

# Override WATCH_DIRECTORY to use a local folder instead of from config
WATCH_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Documents'))

# Initialize FastAPI app
app = FastAPI(title="TalkToFiles")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="frontend/templates")

# Add API routes
app.include_router(api_router, prefix="/api")


# Home page route
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "watch_directory": WATCH_DIRECTORY
    })


# Process existing files in the directory
def process_existing_files(db: QdrantDB, openai_client: AzureOpenAIClient):
    print(f"Processing existing files in {WATCH_DIRECTORY}")
    for file in Path(WATCH_DIRECTORY).glob("*.*"):
        if file.suffix.lower() in ['.pdf', '.txt']:
            print(f"Found existing file: {file}")
            process_file(str(file), db, openai_client)


def process_file(file_path: str, db: QdrantDB, openai_client: AzureOpenAIClient):
    """Process a file and add it to the database"""
    print(f"Processing new file: {file_path}")
    
    # Process the document
    document_chunks = process_document(file_path)
    
    if document_chunks:
        # Extract texts and metadata
        texts = [chunk[0] for chunk in document_chunks]
        metadatas = [chunk[1] for chunk in document_chunks]
        
        # Generate embeddings
        embeddings = openai_client.get_embeddings(texts)
        
        if embeddings:
            # Add texts to database
            db.add_texts(texts, embeddings, metadatas)
            print(f"Added {len(texts)} chunks from {file_path} to the database")
        else:
            print(f"Failed to generate embeddings for {file_path}")
    else:
        print(f"No text chunks extracted from {file_path}")


# Start file watcher
def start_file_watcher(db: QdrantDB, openai_client: AzureOpenAIClient):
    print(f"Starting file watcher for directory: {WATCH_DIRECTORY}")
    
    # Process existing files
    process_existing_files(db, openai_client)
    
    def watch_directory():
        processed_files = set()
        while True:
            for file in Path(WATCH_DIRECTORY).glob("*.*"):
                if file.suffix.lower() in ['.pdf', '.txt'] and str(file) not in processed_files:
                    print(f"Detected new file: {file}")
                    process_file(str(file), db, openai_client)
                    processed_files.add(str(file))
            time.sleep(1)
    
    watcher_thread = threading.Thread(target=watch_directory, daemon=True)
    watcher_thread.start()
    return watcher_thread


if __name__ == "__main__":
    # Ensure the watch directory exists
    os.makedirs(WATCH_DIRECTORY, exist_ok=True)
    
    # Add a sample text file if the directory was just created
    sample_file_path = Path(WATCH_DIRECTORY) / "sample.txt"
    if not sample_file_path.exists():
        with open(sample_file_path, "w", encoding="utf-8") as f:
            f.write("This is a sample text file for TalkToFiles.\n\n")
            f.write("You can add your own PDF or text files to this directory,\n")
            f.write("and they will be automatically processed and made searchable.\n\n")
            f.write("Try asking questions about this text to test the system!")
        print(f"Added sample text file at: {sample_file_path}")
    
    # Initialize clients
    db = QdrantDB()
    openai_client = AzureOpenAIClient()
    
    # Start file watcher in a separate thread
    watcher_thread = start_file_watcher(db, openai_client)
    
    try:
        # Start the API server
        uvicorn.run(app, host=API_HOST, port=API_PORT)
    except KeyboardInterrupt:
        print("Shutting down file watcher...")
    
    watcher_thread.join()