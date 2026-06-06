from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from pymongo import MongoClient
import sys
import os
import logging
import shutil

# Ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from pipeline.rag_chain import LegalRAGChain
from college_intel.report_generator import ReportGenerator
from college_intel.schema import CollegeProfile
from ingestion.loader import PDFLoader
from ingestion.chunker import LegalChunker
from ingestion.embedder import Embedder

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BharatStudent API", version="1.0")


# Initialize modules globally
try:
    rag_chain = LegalRAGChain()
except Exception as e:
    logger.warning(f"RAG Chain initialization failed (Did you run ingestion?): {e}")
    rag_chain = None

report_generator = ReportGenerator()

# MongoDB for direct access in endpoints
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]
collection = db[settings.MONGODB_COLLECTION_NAME]

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: list

class SearchRequest(BaseModel):
    query: str
    state: str = None
    type: str = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(
            status_code=500, 
            detail="RAG system not initialized. Ensure FAISS index is generated via /api/upload."
        )
    try:
        logger.info(f"Processing chat query: {request.query}")
        result = rag_chain.generate_answer(request.query)
        return ChatResponse(answer=result["answer"], sources=result.get("sources", []))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads a PDF and triggers the ingestion pipeline."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    logger.info(f"Uploaded {file.filename}. Triggering ingestion pipeline.")
    
    try:
        loader = PDFLoader()
        documents = loader.load_document(file_path)
        
        chunker = LegalChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        nodes = chunker.get_nodes_from_documents(documents)
        
        embedder = Embedder()
        embedder.embed_and_store(nodes)
        
        # Re-initialize rag chain dynamically
        global rag_chain
        rag_chain = LegalRAGChain()
        
        return {"success": True, "message": f"Successfully ingested {file.filename} with {len(nodes)} chunks."}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/college/{college_name}")
async def get_college_report(college_name: str):
    logger.info(f"Generating report for: {college_name}")
    result = report_generator.generate_report(college_name)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "College not found"))
    return result

@app.post("/api/college/add")
async def add_college(college: CollegeProfile):
    """Add a new college to the MongoDB database."""
    try:
        doc = college.model_dump(exclude={"id"})
        result = collection.insert_one(doc)
        return {"success": True, "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Failed to add college: {e}")
        raise HTTPException(status_code=500, detail="Database insertion failed.")

@app.post("/api/college/search")
async def search_colleges(request: SearchRequest):
    """Search colleges by name and optional state filter."""
    query = {"basic.name": {"$regex": request.query, "$options": "i"}}
    if request.state:
        query["basic.state"] = {"$regex": request.state, "$options": "i"}
    if request.type:
        query["basic.type"] = request.type
        
    results = list(collection.find(query))
    for r in results:
        r["id"] = str(r["_id"])
        del r["_id"]
        
    return {"success": True, "results": results}

# Mount frontend directory for static files at the end to prevent route shadowing
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
