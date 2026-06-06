import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "BharatStudent"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # FastAPI Config
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8080))

    # Streamlit Config
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", 8501))

    # MongoDB Config
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "bharatstudent_db")
    MONGODB_COLLECTION_NAME: str = os.getenv("MONGODB_COLLECTION_NAME", "documents")

    # LlamaIndex / Ollama Config
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "llama3")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", 120))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 600))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 100))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", 5))

    # FAISS Config
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./faiss_indexes/central/index")
    VECTOR_DIMENSIONS: int = int(os.getenv("VECTOR_DIMENSIONS", 768)) # Default for nomic-embed-text

    # PyMuPDF / Document Storage Config
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploaded_pdfs")
    PROCESSED_DATA_DIR: str = os.getenv("PROCESSED_DATA_DIR", "./data/processed")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instantiate settings to be used across the application
settings = Settings()

# Ensure necessary directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
