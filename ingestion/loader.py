import fitz  # PyMuPDF
import os
from typing import List
from llama_index.core import Document
from config import settings

class PDFLoader:
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir

    def load_document(self, file_path: str) -> List[Document]:
        """Loads a single PDF file using PyMuPDF and returns LlamaIndex Documents."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        doc = fitz.open(file_path)
        documents = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            metadata = {
                "source": os.path.basename(file_path),
                "page_number": page_num + 1,
                "total_pages": len(doc)
            }
            documents.append(Document(text=text, metadata=metadata))
            
        return documents

    def load_all(self) -> List[Document]:
        """Loads all PDFs in the upload directory."""
        all_documents = []
        if not os.path.exists(self.upload_dir):
            return all_documents
            
        for filename in os.listdir(self.upload_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(self.upload_dir, filename)
                all_documents.extend(self.load_document(file_path))
        return all_documents
