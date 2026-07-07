import os

class DataLoader:
    """
    Handles reading regulations and policies from text/markdown files and chunking them.
    """
    def __init__(self, chunk_size=512, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text, metadata):
        """
        Splits text into overlapping chunks, preserving metadata.
        For simplicity in this prototype, we chunk by character length.
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })
            if end == text_len:
                break
            start += (self.chunk_size - self.overlap)
            
        return chunks

    def load_directory(self, directory_path):
        """
        Reads all text files in a directory and returns chunks.
        """
        all_chunks = []
        if not os.path.exists(directory_path):
            return all_chunks
            
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.txt') or file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Metadata based on file name (e.g. GDPR_Article_12.txt)
                    source_name = os.path.splitext(file)[0].replace('_', ' ')
                    category = os.path.basename(root)
                    metadata = {
                        "source": source_name,
                        "category": category,
                        "file_path": file_path
                    }
                    
                    chunks = self.chunk_text(content, metadata)
                    all_chunks.extend(chunks)
                    
        return all_chunks
