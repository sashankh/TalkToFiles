from typing import List


def read_txt(file_path: str) -> List[str]:
    """
    Read text from a TXT file and return it as chunks.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        List of text chunks from the TXT file
    """
    chunks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Simple chunking by paragraphs
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                chunks.append(paragraph.strip())
                
        return chunks
    except Exception as e:
        print(f"Error processing TXT file {file_path}: {e}")
        return []