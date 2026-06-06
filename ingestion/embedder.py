import os
import json
import faiss
from typing import List
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import TextNode
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

# Fix absolute import if running from root
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class Embedder:
    def __init__(self):
        # Initialize Ollama Embedding Model (nomic-embed-text)
        self.embed_model = OllamaEmbedding(
            model_name=settings.OLLAMA_EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
        # Initialize FAISS index
        self.d = settings.VECTOR_DIMENSIONS
        self.faiss_index = faiss.IndexFlatL2(self.d)
        self.vector_store = FaissVectorStore(faiss_index=self.faiss_index)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

    def embed_and_store(self, nodes: List[TextNode]):
        """
        Embeds the given nodes, adds them to a FAISS index, and saves the index and metadata to disk.
        """
        print(f"Embedding {len(nodes)} nodes using {settings.OLLAMA_EMBEDDING_MODEL}...")
        
        # Create VectorStoreIndex, which embeds and stores in FAISS
        index = VectorStoreIndex(
            nodes,
            storage_context=self.storage_context,
            embed_model=self.embed_model,
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
        
        # Save FAISS index
        print(f"Saving FAISS index to {settings.FAISS_INDEX_PATH}...")
        self.vector_store.persist(settings.FAISS_INDEX_PATH)
        
        # Save Metadata JSON
        metadata_path = f"{settings.FAISS_INDEX_PATH}_metadata.json"
        
        node_dicts = []
        for node in nodes:
            node_dicts.append({
                "id": node.node_id,
                "text": node.text,
                "metadata": node.metadata
            })
            
        print(f"Saving metadata JSON to {metadata_path}...")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(node_dicts, f, indent=4, ensure_ascii=False)
            
        return index
