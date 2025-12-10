"""
Embeddings Module
Handles generation of embeddings using sentence-transformers (local, free).
"""

import os
from typing import List
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers (local, free, no API needed)."""
    
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model: Sentence transformer model to use (runs locally)
        """
        print(f"Loading embedding model: {model}...")
        self.model_name = model
        self.model = SentenceTransformer(model)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"✓ Initialized embedding generator with model: {model}")
        print(f"✓ Embedding dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts per batch
            
        Returns:
            List of embedding vectors
        """
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"✓ Generated {len(embeddings)} embeddings")
        return embeddings.tolist()

if __name__ == "__main__":
    # Test the embedding generator
    generator = EmbeddingGenerator()
    
    test_texts = [
        "What is economics?",
        "Supply and demand are fundamental economic concepts."
    ]
    
    embeddings = generator.generate_embeddings_batch(test_texts)
    print(f"\nGenerated {len(embeddings)} embeddings")
    print(f"Embedding dimension: {len(embeddings[0])}")
