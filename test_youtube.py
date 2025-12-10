"""
Quick test script to check YouTube transcript extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.youtube_processor import YouTubeProcessor

print("Testing YouTube processor...")

processor = YouTubeProcessor()

# Test both videos
print("\nTesting both videos...")
video_urls = [
    "https://youtu.be/Z_S0VA4jKes",
    "https://youtu.be/Ec19ljjvlCI"
]
chunks = processor.process_videos(video_urls)

print(f"\n✓ Extracted {len(chunks)} chunks total")
if chunks:
    print(f"Sample chunk preview: {chunks[0]['text'][:200]}...")
else:
    print("⚠ No chunks extracted - check video IDs or transcript availability")
