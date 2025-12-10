"""
Main Data Ingestion Pipeline
Orchestrates PDF and YouTube video processing.
"""

import os
import json
from pdf_processor import PDFProcessor
from youtube_processor import YouTubeProcessor


def main():
    """Run the complete data ingestion pipeline."""
    
    print("=" * 60)
    print("NOTEBOOKLM STUDY TOOL - DATA INGESTION")
    print("=" * 60)
    
    # Create output directories
    os.makedirs("data/processed", exist_ok=True)
    
    # Source URLs
    pdf_url = "https://drive.google.com/file/d/1K9tjpEljoDnYXwW1y4jt_gxW1753lxBW/view?usp=drive_link"
    video_urls = [
        "https://youtu.be/Ec19ljjvlCI?list=TLGG6f3IQWMbfUswNDExMjAyNQ",
        "https://www.youtube.com/watch?v=Z_S0VA4jKes"
    ]
    
    # Process PDF
    print("\n" + "=" * 60)
    print("STEP 1: Processing Economics PDF")
    print("=" * 60)
    pdf_processor = PDFProcessor()
    pdf_chunks = pdf_processor.process_pdf(pdf_url)
    
    # Process YouTube videos
    print("\n" + "=" * 60)
    print("STEP 2: Processing YouTube Videos")
    print("=" * 60)
    youtube_processor = YouTubeProcessor()
    video_chunks = youtube_processor.process_videos(video_urls)
    
    # Combine all chunks
    all_chunks = pdf_chunks + video_chunks
    
    # Save processed chunks
    output_file = "data/processed/all_chunks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"✓ Total chunks processed: {len(all_chunks)}")
    print(f"  - PDF chunks: {len(pdf_chunks)}")
    print(f"  - YouTube chunks: {len(video_chunks)}")
    print(f"\n✓ Saved to: {output_file}")
    print("\nNext step: Run the embedding generation to create vector store")
    print("=" * 60)
    
    return all_chunks


if __name__ == "__main__":
    main()
