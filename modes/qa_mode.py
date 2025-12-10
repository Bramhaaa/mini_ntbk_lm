"""
Q&A Mode
Standard question-answering using RAG.
"""

from typing import Dict, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.retriever import RAGRetriever


class QAMode:
    """Question and Answer mode using RAG."""
    
    def __init__(self, retriever: RAGRetriever):
        """
        Initialize Q&A mode.
        
        Args:
            retriever: RAGRetriever instance
        """
        self.retriever = retriever
    
    def ask_question(self, question: str, k: int = 5) -> Dict[str, any]:
        """
        Ask a question and get a grounded answer.
        
        Args:
            question: User's question
            k: Number of source chunks to retrieve
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        result = self.retriever.answer_question(question, k=k)
        
        # Format sources for display
        formatted_sources = []
        for i, source in enumerate(result['sources'], 1):
            source_info = {
                'number': i,
                'type': source.get('type', 'unknown'),
                'source_name': source.get('source', 'unknown'),
                'text_preview': source['text'][:200] + "..." if len(source['text']) > 200 else source['text'],
                'similarity_score': source.get('similarity_score', 0)
            }
            formatted_sources.append(source_info)
        
        return {
            'question': question,
            'answer': result['answer'],
            'sources': formatted_sources,
            'num_sources': len(formatted_sources)
        }
    
    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions for the user."""
        return [
            "What is economics and why is it important?",
            "Explain the concept of supply and demand",
            "What are the factors of production?",
            "How do markets allocate resources?",
            "What is the difference between microeconomics and macroeconomics?",
            "Explain opportunity cost with an example",
            "What role does government play in the economy?",
            "How do incentives affect economic behavior?"
        ]


if __name__ == "__main__":
    from rag.embeddings import EmbeddingGenerator
    from rag.vector_store import VectorStore
    
    # Test Q&A mode
    generator = EmbeddingGenerator()
    store = VectorStore()
    
    if store.exists():
        store.load(generator)
        retriever = RAGRetriever(store)
        qa = QAMode(retriever)
        
        test_question = "What is economics?"
        result = qa.ask_question(test_question)
        
        print(f"Question: {result['question']}")
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources: {result['num_sources']}")
    else:
        print("Vector store not found. Please run build_vector_store.py first.")
