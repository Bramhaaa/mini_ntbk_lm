"""
Build Vector Store
Creates embeddings and FAISS index from processed chunks.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore


def main():
    """Build vector store from processed chunks."""
    
    print("=" * 60)
    print("BUILDING VECTOR STORE")
    print("=" * 60)
    
    # Check if chunks exist
    chunks_file = "data/processed/all_chunks.json"
    if not os.path.exists(chunks_file):
        print(f"\n✗ Error: Chunks file not found at {chunks_file}")
        print("Please run ingestion/ingest_data.py first")
        return
    
    # Load chunks
    print(f"\nLoading chunks from {chunks_file}...")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✓ Loaded {len(chunks)} chunks")
    
    # Initialize embedding generator
    print("\nInitializing embedding generator...")
    generator = EmbeddingGenerator()
    
    # Build vector store
    store = VectorStore()
    store.build_index(chunks, generator)
    
    print("\n" + "=" * 60)
    print("VECTOR STORE BUILD COMPLETE")
    print("=" * 60)
    print("\nYou can now run the application:")
    print("  streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
