"""
Video Summary Mode
Generates structured video-style summaries of chapter content.
"""

import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.retriever import RAGRetriever

load_dotenv()


class VideoSummaryMode:
    """Generate video-style structured summaries."""
    
    def __init__(self, retriever: RAGRetriever):
        """
        Initialize video summary mode.
        
        Args:
            retriever: RAGRetriever instance
        """
        self.retriever = retriever
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def generate_summary(self, topic: str = "Chapter Overview") -> Dict[str, any]:
        """
        Generate a comprehensive video-style summary.
        
        Args:
            topic: Topic or section to summarize
            
        Returns:
            Dictionary with structured summary sections
        """
        # Retrieve comprehensive context
        context, sources = self.retriever.retrieve_context(topic, k=15)
        
        # System prompt for video summary generation
        system_prompt = """You are creating a structured video-style educational summary for economics content.

Generate a comprehensive, well-structured summary organized as if it were a presentation or educational video.

Structure your output with these sections:

# 📚 CHAPTER OVERVIEW
[Broad introduction to the chapter/topic]

# 🎯 KEY LEARNING OBJECTIVES
- Objective 1
- Objective 2
- Objective 3
[etc.]

# 📖 CORE CONCEPTS

## Concept 1: [Name]
**Definition:** [Clear definition]
**Explanation:** [Detailed explanation]
**Key Points:**
- Point 1
- Point 2
**Real-World Example:** [Example from sources if available]

## Concept 2: [Name]
[Same structure]

[Continue for all major concepts]

# 📊 VISUAL REPRESENTATIONS
[Describe key graphs, models, or diagrams mentioned in the sources]

Example:
**Supply and Demand Curve:**
- Description of what it shows
- Key insights
- How to interpret it

# 💡 IMPORTANT DEFINITIONS
- **Term 1:** Definition
- **Term 2:** Definition
[All key terms]

# 🌍 REAL-WORLD APPLICATIONS
[How these concepts apply to real economic situations]

# ⚡ EXAM TIPS & KEY TAKEAWAYS
- Quick revision point 1
- Quick revision point 2
- Common mistakes to avoid
- What examiners look for

# 🔗 CONNECTIONS TO OTHER TOPICS
[How this topic relates to other economic concepts]

Rules:
1. Base ALL content strictly on the provided sources
2. Be comprehensive and educational
3. Use clear, structured formatting
4. Include all relevant details from sources
5. Make it suitable for visual presentation
6. Focus on clarity and learning

Context:
{context}"""
        
        # Generate summary
        full_prompt = f"""{system_prompt}

Create a comprehensive video-style summary for: {topic}"""
        
        response = self.model.generate_content(full_prompt)
        summary = response.text
        
        return {
            'topic': topic,
            'summary': summary,
            'sources': sources,
            'num_sources': len(sources)
        }
    
    def generate_section_summary(self, section_name: str) -> Dict[str, any]:
        """
        Generate summary for a specific section.
        
        Args:
            section_name: Name of the section
            
        Returns:
            Focused summary for that section
        """
        return self.generate_summary(topic=section_name)
    
    def get_suggested_sections(self) -> List[str]:
        """Get suggested sections to summarize."""
        return [
            "Complete Chapter Overview",
            "Introduction to Economics",
            "Fundamental Economic Concepts",
            "Supply and Demand",
            "Market Structures",
            "Production and Costs",
            "Economic Systems",
            "Government and Economics"
        ]


if __name__ == "__main__":
    from rag.embeddings import EmbeddingGenerator
    from rag.vector_store import VectorStore
    
    # Test video summary mode
    generator = EmbeddingGenerator()
    store = VectorStore()
    
    if store.exists():
        store.load(generator)
        retriever = RAGRetriever(store)
        video_mode = VideoSummaryMode(retriever)
        
        result = video_mode.generate_summary("Economics Fundamentals")
        
        print(f"Topic: {result['topic']}")
        print(f"\nSummary:\n{result['summary']}")
        print(f"\nBased on {result['num_sources']} sources")
    else:
        print("Vector store not found. Please run build_vector_store.py first.")
