import os
from pathlib import Path
from typing import Dict, List, Tuple
import datetime

from file_processing.pdf_reader import read_pdf
from file_processing.txt_reader import read_txt


def process_document(file_path: str) -> List[Tuple[str, str]]:
    """
    Process a document and extract text chunks with metadata
    
    Args:
        file_path: Path to the document
        
    Returns:
        List of tuples containing (text_chunk, metadata)
    """
    file_path = Path(file_path)
    file_name = file_path.name
    file_ext = file_path.suffix.lower()
    
    chunks = []
    
    if file_ext == '.pdf':
        text_chunks = read_pdf(str(file_path))
    elif file_ext == '.txt':
        text_chunks = read_txt(str(file_path))
    else:
        print(f"Unsupported file type: {file_ext}")
        return []
    
    # Add metadata to each chunk
    result = []
    for i, chunk in enumerate(text_chunks):
        metadata = {
            "source": str(file_path),  # Store the full path
            "title": file_name,  # Add a title field for display purposes
            "chunk_id": i,
            "file_type": file_ext,
            "timestamp": datetime.datetime.now().isoformat()  # Add timestamp for sorting
        }
        result.append((chunk, metadata))
    
    return result