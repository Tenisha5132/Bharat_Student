# 🎓 BharatStudent — AI-Powered Student Rights & College Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-6.0+-47A248?logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/LlamaIndex-RAG-FF6F00" />
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-blue" />
</p>

**BharatStudent** is a production-grade AI platform that empowers Indian students with two core capabilities:

1. **Legal Rights RAG Assistant** — Upload UGC/AICTE regulation PDFs and ask natural-language questions. The AI returns precise, citation-backed answers with document source, page number, and legal section references.
2. **College Intelligence Dashboard** — Search and vet any Indian college with a dynamically computed **Trust Score (0–10)**, backed by regulatory data, placement stats, fee analysis, and AI-generated intelligence reports.

---

## ✨ Key Features

### ⚖️ Mode 1: Student Rights Assistant (RAG Pipeline)
- **PDF Ingestion** — Drag-and-drop UGC/AICTE/University handbook PDFs via the web UI
- **FAISS Vector Search** — Documents are chunked, embedded, and stored in a local FAISS index for fast semantic retrieval
- **Citation-Backed Answers** — Every response includes the exact document name, page number, and legal section
- **Graceful Degradation** — If the local LLM (Ollama) is offline, the system returns relevant document chunks as a structured fallback

### 🏫 Mode 2: College Intelligence Engine
- **MongoDB-Backed Directory** — Search colleges by name, state, or institution type
- **Trust Score Algorithm** — Dynamically calculated score incorporating:
  - NAAC Grade Scaling (30%)
  - AICTE/UGC Regulatory Approval (20%)
  - Student Review Sentiment (20%)
  - Red Flag Penalization (-30%)
- **AI Intelligence Reports** — Llama 3 analyzes fees, placements, and regulatory data to generate a comprehensive markdown report
- **Fallback Report Generator** — If LLM is unavailable, a structured template-based report is auto-generated from the database

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| **Backend** | FastAPI (Python 3.10+) |
| **Frontend** | Vanilla HTML/CSS/JS (served as static files by FastAPI) |
| **Vector DB** | FAISS (`faiss-cpu`) |
| **Document DB** | MongoDB 6.0+ |
| **RAG Framework** | LlamaIndex |
| **LLM** | Ollama (Llama 3) — *optional, fallback built-in* |
| **Embeddings** | Ollama (`nomic-embed-text`) or HuggingFace Sentence Transformers |

---

## 📂 Project Structure

```
RAG/
├── api/
│   └── main.py              # FastAPI app — all API routes + static file serving
├── frontend/
│   ├── index.html            # Landing page
│   ├── chat.html             # Legal Rights AI chat interface
│   ├── upload.html           # Drag-and-drop PDF ingestion page
│   ├── search.html           # College vetting directory + report modal
│   ├── styles.css            # Full design system (Inter font, saffron-navy theme)
│   └── app.js                # Shared frontend utilities (navbar scroll, etc.)
├── pipeline/
│   └── rag_chain.py          # RAG retrieval + LLM answer generation (with fallback)
├── ingestion/
│   └── ingest.py             # PDF chunking and FAISS index builder
├── retrieval/
│   └── retriever.py          # FAISS-backed document retriever
├── college_intel/
│   ├── models.py             # Pydantic models for college profiles
│   ├── scoring.py            # Trust Score computation engine
│   └── report_generator.py   # LLM + fallback report generator
├── config.py                 # Central configuration (ports, paths, DB URI)
├── db_seed.py                # MongoDB seeder with 5 test colleges
├── requirements.txt          # Python dependencies
├── data/
│   ├── uploaded_pdfs/        # Uploaded regulation documents
│   └── processed/            # Processed document chunks
├── faiss_indexes/
│   └── central/              # FAISS vector index (generated after ingestion)
└── README.md
```

---

## 🚀 Local Setup (No Docker Required)

### Prerequisites
- **Python 3.10+**
- **MongoDB** — Running locally on `localhost:27017`
- **Ollama** *(optional)* — For full AI responses. Without it, the platform uses built-in fallbacks.

### Step 1: Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Seed the Database
Populate MongoDB with 5 test colleges (Telangana, Maharashtra, Tamil Nadu, Delhi):
```bash
python db_seed.py
```

### Step 3: Start the Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8080
```

### Step 4: Open the Platform
Navigate to **[http://localhost:8080](http://localhost:8080)** in your browser.

### Step 5: Ingest a PDF (First Time)
Upload a regulation PDF via the **Upload** page or via curl:
```bash
curl -X POST "http://localhost:8080/api/upload" -F "file=@path/to/your/document.pdf"
```
This builds the FAISS index under `faiss_indexes/central/`. The chat assistant becomes active after this step.

### (Optional) Enable Full AI
Install and start Ollama for LLM-powered responses:
```bash
ollama run llama3
ollama run nomic-embed-text
```

---

## 🔌 API Reference

All endpoints are served at `http://localhost:8080`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Submit a legal query to the RAG assistant |
| `POST` | `/api/upload` | Upload and ingest a PDF into the FAISS index |
| `GET` | `/api/college/{name}` | Get full AI intelligence report + trust score |
| `POST` | `/api/college/search` | Search colleges by name, state, or type |
| `POST` | `/api/college/add` | Insert a new college into the database |

### Example: Chat Query
```bash
curl -X POST "http://localhost:8080/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are my rights if a college holds my original certificates?"}'
```

### Example: College Search
```bash
curl -X POST "http://localhost:8080/api/college/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "Engineering", "state": "Telangana"}'
```

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (Static HTML/CSS/JS)          │
│   index.html  │  chat.html  │  upload.html  │ search.html│
└───────────────────────┬──────────────────────────────────┘
                        │ HTTP
                        ▼
┌──────────────────────────────────────────────────────────┐
│              FastAPI Backend (api/main.py)                │
│  ┌──────────┐  ┌───────────────┐  ┌───────────────────┐  │
│  │ /api/chat│  │ /api/upload   │  │ /api/college/*    │  │
│  └────┬─────┘  └───────┬───────┘  └────────┬──────────┘  │
│       │                │                   │              │
│       ▼                ▼                   ▼              │
│  ┌─────────┐    ┌───────────┐    ┌─────────────────┐     │
│  │RAG Chain│    │ Ingestion │    │ College Intel    │     │
│  │(LlamaIdx│    │ Pipeline  │    │ (Scoring +       │     │
│  │+Fallback)│   │(PDF→FAISS)│    │  Report Gen)     │     │
│  └────┬─────┘   └─────┬─────┘   └────────┬─────────┘    │
│       │               │                   │               │
│       ▼               ▼                   ▼               │
│  ┌─────────┐    ┌──────────┐      ┌───────────┐          │
│  │  FAISS  │    │  FAISS   │      │  MongoDB  │          │
│  │ (Query) │    │ (Write)  │      │           │          │
│  └─────────┘    └──────────┘      └───────────┘          │
│       │                                                   │
│       ▼ (optional)                                        │
│  ┌──────────┐                                             │
│  │  Ollama  │  ← LLM + Embeddings (graceful fallback)    │
│  └──────────┘                                             │
└──────────────────────────────────────────────────────────┘
```

---

## 📜 License

This project is built for educational and research purposes.

---

<p align="center">
  Built with ❤️ for the students of India
</p>
