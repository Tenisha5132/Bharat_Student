import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any
from llama_index.embeddings.ollama import OllamaEmbedding

# Fix absolute import if running from root
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class FAISSRetriever:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.embed_model = OllamaEmbedding(
            model_name=settings.OLLAMA_EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
        
        # Ensure paths exist before loading
        if not os.path.exists(settings.FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found at {settings.FAISS_INDEX_PATH}. Please run ingestion first.")
            
        metadata_path = f"{settings.FAISS_INDEX_PATH}_metadata.json"
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata JSON not found at {metadata_path}. Please run ingestion first.")
            
        # Load FAISS index directly
        self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
        
        # Load metadata JSON
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata_store = json.load(f)
            
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Embeds the query, searches the FAISS index, and returns the top_k chunks
        with their source and page metadata.
        """
        # Embed query
        query_embedding = self.embed_model.get_text_embedding(query)
        
        # FAISS requires a 2D numpy array of float32
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search FAISS (distances are L2, so lower is better)
        distances, indices = self.index.search(query_vector, self.top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue # Not enough results in index
                
            # The indices in FAISS match the insertion order of our metadata JSON array
            node_data = self.metadata_store[idx]
            
            # Extract metadata safely
            meta = node_data.get("metadata", {})
            
            result = {
                "text": node_data["text"],
                "score": float(distances[0][i]),
                "source": meta.get("source", "Unknown Source"),
                "page": meta.get("page_number", "Unknown Page"),
                "legal_section": meta.get("legal_section", "General")
            }
            results.append(result)
            
        return results
