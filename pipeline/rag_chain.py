import os
import sys
from typing import Dict, Any
from llama_index.llms.ollama import Ollama

# Fix absolute import if running from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from retrieval.retriever import FAISSRetriever

class LegalRAGChain:
    def __init__(self):
        self.retriever = FAISSRetriever(top_k=5)
        
        # Initialize Llama 3 via Ollama
        self.llm = Ollama(
            model=settings.OLLAMA_LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            request_timeout=settings.LLM_TIMEOUT,
        )
        
        self.system_prompt = """You are an expert Legal Assistant for the BharatStudent project. 
Your task is to answer the user's questions based ONLY on the provided legal documents.
You must be precise, professional, and directly address the query.

CRITICAL INSTRUCTION: You MUST cite your sources for every factual claim you make.
Use the format: [Source: <filename>, Page: <page>, Section: <section>] immediately after the claim.
If the answer is not contained within the provided context, state clearly that you do not have enough information to answer.
Do not use outside knowledge.
"""

    def generate_answer(self, query: str) -> Dict[str, Any]:
        """
        Runs the RAG pipeline: retrieves chunks and generates a cited answer.
        """
        # 1. Retrieve relevant chunks
        chunks = self.retriever.retrieve(query)
        
        if not chunks:
            return {
                "answer": "No relevant documents found in the database to answer your query. Please ensure documents have been ingested.",
                "sources": []
            }
            
        # 2. Format context for the LLM
        context_parts = []
        for i, chunk in enumerate(chunks):
            source_info = f"Source: {chunk['source']}, Page: {chunk['page']}, Section: {chunk['legal_section']}"
            context_parts.append(f"--- Document Chunk {i+1} ---\n{source_info}\nText:\n{chunk['text']}")
            
        context_str = "\n\n".join(context_parts)
        
        # 3. Construct the prompt
        prompt = f"""{self.system_prompt}

====================
CONTEXT INFORMATION:
====================
{context_str}

====================
USER QUERY: 
====================
{query}

Please provide your answer with mandatory citations based on the context above:
"""

        # 4. Generate response
        try:
            print(f"Querying LLM ({settings.OLLAMA_LLM_MODEL})...")
            response = self.llm.complete(prompt)
            answer = str(response)
        except Exception as e:
            print(f"Ollama complete failed: {e}. Falling back to context snippet extraction.")
            # Graceful fallback: synthesize a simple answer from the top chunks
            answer = "⚠️ **[Local LLM Offline]** Could not connect to Ollama (Llama 3). Here are the exact matching clauses retrieved from your documents:\n\n"
            for i, chunk in enumerate(chunks[:3]):
                answer += f"📄 **{chunk['source']} (Page {chunk['page']}, Section {chunk['legal_section']})**:\n> \"{chunk['text'][:400]}...\"\n\n"
            answer += "\n\n*To enable AI-synthesized responses, please ensure Ollama is installed and running with `ollama run llama3`.*"
        
        return {
            "answer": answer,
            "sources": chunks
        }

