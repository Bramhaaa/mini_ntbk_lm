"""
RAG Retriever Module
Handles retrieval-augmented generation logic.
"""

import os
from typing import List, Dict, Tuple
import google.generativeai as genai
from dotenv import load_dotenv
from .vector_store import VectorStore
from .embeddings import EmbeddingGenerator

load_dotenv()


class RAGRetriever:
    """Retrieval-Augmented Generation system."""
    
    def __init__(self, vector_store: VectorStore, model: str = "gemini-2.5-flash"):
        """
        Initialize RAG retriever.
        
        Args:
            vector_store: VectorStore instance
            model: Google Gemini chat model to use
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.vector_store = vector_store
        self.model_name = model
        print(f"✓ Initialized RAG retriever with model: {model}")
    
    def retrieve_context(self, query: str, k: int = 5) -> Tuple[str, List[Dict]]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            k: Number of chunks to retrieve
            
        Returns:
            Tuple of (formatted_context, source_chunks)
        """
        results = self.vector_store.search(query, k=k)
        
        # Format context
        context_parts = []
        for i, chunk in enumerate(results, 1):
            source_type = chunk.get('type', 'unknown')
            source = chunk.get('source', 'unknown')
            text = chunk['text']
            
            context_parts.append(f"[Source {i} - {source_type}]:\n{text}")
        
        formatted_context = "\n\n".join(context_parts)
        
        return formatted_context, results
    
    def generate_response(self, query: str, context: str, system_prompt: str) -> str:
        """
        Generate response using retrieved context.
        
        Args:
            query: User query
            context: Retrieved context
            system_prompt: System instructions
            
        Returns:
            Generated response
        """
        # Combine system prompt and user query for Gemini
        full_prompt = f"""{system_prompt}

Context:
{context}

Question: {query}

Answer:"""
        
        response = self.model.generate_content(full_prompt)
        
        return response.text
    
    def answer_question(self, query: str, k: int = 5) -> Dict[str, any]:
        """
        Complete RAG pipeline: retrieve and generate answer.
        
        Args:
            query: User question
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve context
        context, sources = self.retrieve_context(query, k=k)
        
        # System prompt for Q&A mode
        system_prompt = """You are a friendly, helpful economics teacher having a natural conversation with a student. 

Rules:
1. Be conversational and warm - respond like a real teacher chatting with a student
2. Use the provided context to inform your answers, but don't cite sources explicitly (no "according to Source 1")
3. If continuing a conversation, acknowledge what was discussed before
4. Keep responses concise and natural (2-4 sentences usually)
5. Use casual language like "Hey!", "Great question!", "Actually...", "You know what's interesting..."
6. If you don't have info in the materials, say something like "Hmm, I don't have that specific info in our course materials"
7. Never be formal or list-like - just chat naturally"""
        
        # Generate answer
        answer = self.generate_response(query, context, system_prompt)
        
        return {
            'answer': answer,
            'sources': sources,
            'query': query
        }


if __name__ == "__main__":
    # Test RAG retriever
    generator = EmbeddingGenerator()
    store = VectorStore()
    
    # Check if vector store exists
    if store.exists():
        store.load(generator)
        retriever = RAGRetriever(store)
        
        test_query = "What is economics?"
        result = retriever.answer_question(test_query)
        
        print(f"\nQuery: {result['query']}")
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources used: {len(result['sources'])}")
    else:
        print("Vector store not found. Please run ingestion first.")
