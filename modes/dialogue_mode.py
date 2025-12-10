"""
Dialogue Mode
Two-person dialogue simulation (Student/Teacher format).
"""

import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.retriever import RAGRetriever

load_dotenv()


class DialogueMode:
    """Interactive dialogue tutor mode (Student/Teacher conversation)."""
    
    def __init__(self, retriever: RAGRetriever):
        """
        Initialize dialogue mode.
        
        Args:
            retriever: RAGRetriever instance
        """
        self.retriever = retriever
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")
    
    def generate_dialogue(self, topic: str, num_exchanges: int = 5) -> Dict[str, any]:
        """
        Generate a two-person dialogue about a topic.
        
        Args:
            topic: Topic to discuss
            num_exchanges: Number of student-teacher exchanges
            
        Returns:
            Dictionary with dialogue and sources
        """
        # Retrieve relevant context
        context, sources = self.retriever.retrieve_context(topic, k=8)
        
        # System prompt for dialogue generation
        system_prompt = f"""You are generating an educational dialogue between a Student and a Teacher about economics.

STRICT FORMAT REQUIREMENT:
You MUST output ONLY the dialogue in this exact format:
Student: [student's question or comment]
Teacher: [teacher's explanation]
Student: [follow-up question]
Teacher: [further explanation]
...and so on.

Rules:
1. Generate EXACTLY {num_exchanges} exchanges (Student-Teacher pairs)
2. Base ALL content ONLY on the provided context
3. The Student asks questions progressing from basic to more detailed
4. The Teacher provides clear, educational explanations using ONLY information from the sources
5. Include examples and clarifications from the source materials
6. Make it conversational and natural
7. Build each exchange on the previous one
8. Do NOT add any text outside the Student:/Teacher: format
9. Do NOT add introductions, conclusions, or meta-commentary

Context from sources:
{context}

Topic: {topic}"""
        
        # Generate dialogue
        full_prompt = f"""{system_prompt}

Generate a {num_exchanges}-exchange educational dialogue about: {topic}"""
        
        response = self.model.generate_content(full_prompt)
        dialogue = response.text
        
        # Parse dialogue into structured format
        lines = dialogue.strip().split('\n')
        exchanges = []
        current_exchange = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Student:'):
                if current_exchange.get('teacher'):
                    exchanges.append(current_exchange)
                    current_exchange = {}
                current_exchange['student'] = line.replace('Student:', '').strip()
            elif line.startswith('Teacher:'):
                current_exchange['teacher'] = line.replace('Teacher:', '').strip()
        
        # Add last exchange
        if current_exchange.get('teacher'):
            exchanges.append(current_exchange)
        
        return {
            'topic': topic,
            'dialogue_text': dialogue,
            'exchanges': exchanges,
            'num_exchanges': len(exchanges),
            'sources': sources
        }
    
    def get_suggested_topics(self) -> List[str]:
        """Get suggested dialogue topics."""
        return [
            "Introduction to Economics",
            "Supply and Demand Fundamentals",
            "Opportunity Cost and Trade-offs",
            "Market Equilibrium",
            "Factors of Production",
            "Economic Systems",
            "Role of Government in Economy",
            "Incentives and Decision Making"
        ]


if __name__ == "__main__":
    from rag.embeddings import EmbeddingGenerator
    from rag.vector_store import VectorStore
    
    # Test dialogue mode
    generator = EmbeddingGenerator()
    store = VectorStore()
    
    if store.exists():
        store.load(generator)
        retriever = RAGRetriever(store)
        dialogue = DialogueMode(retriever)
        
        result = dialogue.generate_dialogue("Supply and Demand", num_exchanges=3)
        
        print(f"Topic: {result['topic']}")
        print(f"\nDialogue:\n{result['dialogue_text']}")
        print(f"\nExchanges: {result['num_exchanges']}")
    else:
        print("Vector store not found. Please run build_vector_store.py first.")
