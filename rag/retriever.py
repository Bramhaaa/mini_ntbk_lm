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
    
    def __init__(self, vector_store: VectorStore, model: str = "gemini-pro"):
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
        system_prompt = """You are an expert economics tutor. Answer questions based ONLY on the provided context from the economics chapter and video transcripts.

Rules:
1. Ground all answers strictly in the provided sources
2. If information is not in the sources, say "I don't have enough information in the provided materials to answer this"
3. Cite which sources you're using (PDF or video transcript)
4. Be clear, concise, and educational
5. Use examples from the sources when available
6. Never make up information or use external knowledge"""
        
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
