"""
Embeddings Module
Handles generation of embeddings using OpenAI API.
"""

import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class EmbeddingGenerator:
    """Generate embeddings using OpenAI's embedding models."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize embedding generator.
        
        Args:
            model: OpenAI embedding model to use
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        print(f"✓ Initialized embedding generator with model: {model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts per batch
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
        
        print(f"✓ Generated {len(embeddings)} embeddings")
        return embeddings


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
