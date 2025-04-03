import PyPDF2
from pathlib import Path
from typing import List


def read_pdf(file_path: str) -> List[str]:
    """
    Extract text from a PDF file and return it as chunks.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of text chunks from the PDF
    """
    chunks = []
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    # Add page metadata to the chunk
                    chunk = f"Page {i+1}: {text}"
                    chunks.append(chunk)
        return chunks
    except Exception as e:
        print(f"Error processing PDF file {file_path}: {e}")
        return []