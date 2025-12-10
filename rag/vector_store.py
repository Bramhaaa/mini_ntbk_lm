"""
Vector Store Module
Manages FAISS vector database for similarity search.
"""

import os
import json
import pickle
import numpy as np
import faiss
from typing import List, Dict, Tuple
from .embeddings import EmbeddingGenerator


class VectorStore:
    """FAISS-based vector store for semantic search."""
    
    def __init__(self, dimension: int = None, store_dir: str = "data/vector_store"):
        """
        Initialize vector store.
        
        Args:
            dimension: Embedding vector dimension (auto-detected if None)
            store_dir: Directory to save/load vector store
        """
        self.dimension = dimension
        self.store_dir = store_dir
        self.index = None
        self.chunks = []
        self.embedding_generator = None
        
        os.makedirs(store_dir, exist_ok=True)
    
    def build_index(self, chunks: List[Dict[str, str]], embedding_generator: EmbeddingGenerator):
        """
        Build FAISS index from chunks.
        
        Args:
            chunks: List of text chunks with metadata
            embedding_generator: EmbeddingGenerator instance
        """
        print("\n" + "=" * 60)
        print("Building Vector Store")
        print("=" * 60)
        
        self.embedding_generator = embedding_generator
        self.chunks = chunks
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        print(f"\nGenerating embeddings for {len(texts)} chunks...")
        embeddings = embedding_generator.generate_embeddings_batch(texts)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Auto-detect dimension if not set
        if self.dimension is None:
            self.dimension = embeddings_array.shape[1]
            print(f"✓ Auto-detected embedding dimension: {self.dimension}")
        
        # Create FAISS index
        print("\nCreating FAISS index...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        print(f"✓ Added {self.index.ntotal} vectors to index")
        
        # Save index
        self.save()
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, any]]:
        """
        Search for similar chunks.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant chunks with scores
        """
        if self.index is None:
            raise ValueError("Index not built or loaded")
        
        if self.embedding_generator is None:
            raise ValueError("Embedding generator not initialized")
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_vector, k)
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                result = self.chunks[idx].copy()
                result['similarity_score'] = float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                results.append(result)
        
        return results
    
    def save(self):
        """Save vector store to disk."""
        # Save FAISS index
        index_path = os.path.join(self.store_dir, "faiss_index.bin")
        faiss.write_index(self.index, index_path)
        
        # Save chunks metadata
        chunks_path = os.path.join(self.store_dir, "chunks.pkl")
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        print(f"\n✓ Saved vector store to: {self.store_dir}")
    
    def load(self, embedding_generator: EmbeddingGenerator):
        """
        Load vector store from disk.
        
        Args:
            embedding_generator: EmbeddingGenerator instance
        """
        # Load FAISS index
        index_path = os.path.join(self.store_dir, "faiss_index.bin")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found at {index_path}")
        
        self.index = faiss.read_index(index_path)
        
        # Load chunks
        chunks_path = os.path.join(self.store_dir, "chunks.pkl")
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)
        
        self.embedding_generator = embedding_generator
        
        print(f"✓ Loaded vector store with {self.index.ntotal} vectors")
    
    def exists(self) -> bool:
        """Check if vector store exists on disk."""
        index_path = os.path.join(self.store_dir, "faiss_index.bin")
        chunks_path = os.path.join(self.store_dir, "chunks.pkl")
        return os.path.exists(index_path) and os.path.exists(chunks_path)


if __name__ == "__main__":
    # Test vector store
    from embeddings import EmbeddingGenerator
    
    # Create sample chunks
    test_chunks = [
        {"id": "1", "text": "Economics is the study of how people allocate scarce resources.", "source": "test"},
        {"id": "2", "text": "Supply and demand determine market prices.", "source": "test"},
        {"id": "3", "text": "GDP measures the total economic output of a country.", "source": "test"},
    ]
    
    # Build index
    generator = EmbeddingGenerator()
    store = VectorStore()
    store.build_index(test_chunks, generator)
    
    # Test search
    results = store.search("What is economics?", k=2)
    print(f"\nSearch results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['similarity_score']:.3f}")
        print(f"   Text: {result['text'][:80]}...")
