"""
YouTube Processor Module
Handles extraction and processing of YouTube video transcripts.
"""

import os
import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class YouTubeProcessor:
    """Process YouTube video transcripts."""
    
    def __init__(self, output_dir: str = "data/downloads"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL (various formats supported)
            
        Returns:
            Video ID
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_transcript(self, video_url: str, timeout: int = 30) -> str:
        """
        Fetch transcript from YouTube video with timeout.
        
        Args:
            video_url: YouTube video URL
            timeout: Timeout in seconds
            
        Returns:
            Full transcript text
        """
        video_id = self.extract_video_id(video_url)
        print(f"  Fetching transcript for video {video_id}...")
        
        try:
            # Create API instance and fetch transcript
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=['en'])
            
            # Combine all text segments
            full_text = " ".join([entry.text for entry in transcript_list])
            
            print(f"  ✓ Extracted transcript from video {video_id} ({len(transcript_list)} segments)")
            return full_text
            
        except TranscriptsDisabled:
            print(f"  ✗ Transcripts are disabled for video {video_id}")
            return ""
        except NoTranscriptFound:
            print(f"  ✗ No English transcript found for video {video_id}")
            # Try auto-generated (any language)
            try:
                print(f"  → Trying auto-generated transcript...")
                api = YouTubeTranscriptApi()
                transcript_list = api.fetch(video_id)
                full_text = " ".join([entry.text for entry in transcript_list])
                print(f"  ✓ Extracted auto-generated transcript ({len(transcript_list)} segments)")
                return full_text
            except:
                return ""
        except Exception as e:
            print(f"  ✗ Error extracting transcript: {str(e)}")
            return ""
    
    def chunk_transcript(self, text: str, video_url: str, chunk_size: int = 800, overlap: int = 150) -> List[Dict[str, str]]:
        """
        Split transcript into overlapping chunks.
        
        Args:
            text: Full transcript text
            video_url: Source video URL
            chunk_size: Target chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries
        """
        if not text:
            return []
        
        print(f"  Chunking transcript (length: {len(text)} characters)...")
        
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\[.*?\]', '', text)  # Remove timestamp markers
        
        video_id = self.extract_video_id(video_url)
        chunks = []
        start = 0
        chunk_id = 0
        # Safety limit: max chunks based on text length and chunk size
        max_chunks = (len(text) // (chunk_size - overlap)) + 10
        
        while start < len(text) and chunk_id < max_chunks:
            end = min(start + chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                period_pos = text.rfind('.', start, end)
                question_pos = text.rfind('?', start, end)
                exclaim_pos = text.rfind('!', start, end)
                
                best_pos = max(period_pos, question_pos, exclaim_pos)
                if best_pos > start:
                    end = best_pos + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'id': f'youtube_{video_id}_chunk_{chunk_id}',
                    'text': chunk_text,
                    'source': f'youtube_video_{video_id}',
                    'type': 'youtube',
                    'video_url': video_url,
                    'chunk_index': chunk_id
                })
                chunk_id += 1
            
            # Move forward, ensure we make progress
            if end <= start:
                start += chunk_size
            else:
                start = end - overlap
        
        print(f"  ✓ Created {len(chunks)} chunks from video transcript")
        return chunks
    
    def process_video(self, video_url: str) -> List[Dict[str, str]]:
        """
        Complete pipeline: fetch transcript and chunk it.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            List of transcript chunks with metadata
        """
        print(f"\n🎥 Processing YouTube video: {video_url}")
        transcript = self.get_transcript(video_url)
        
        if not transcript:
            print("⚠ Warning: Could not extract transcript")
            return []
        
        chunks = self.chunk_transcript(transcript, video_url)
        return chunks
    
    def process_videos(self, video_urls: List[str]) -> List[Dict[str, str]]:
        """
        Process multiple YouTube videos with error handling.
        
        Args:
            video_urls: List of YouTube URLs
            
        Returns:
            Combined list of all chunks
        """
        all_chunks = []
        success_count = 0
        
        for i, url in enumerate(video_urls, 1):
            print(f"\n[Video {i}/{len(video_urls)}]")
            try:
                chunks = self.process_video(url)
                if chunks:
                    all_chunks.extend(chunks)
                    success_count += 1
                else:
                    print(f"⚠ Skipping video (no transcript available)")
            except Exception as e:
                print(f"✗ Error processing video: {str(e)}")
                print(f"⚠ Skipping this video and continuing...")
        
        print(f"\n✓ Total chunks from all videos: {len(all_chunks)}")
        return all_chunks


if __name__ == "__main__":
    # Test the processor
    processor = YouTubeProcessor()
    
    video_urls = [
        "https://youtu.be/Ec19ljjvlCI?list=TLGG6f3IQWMbfUswNDExMjAyNQ",
        "https://www.youtube.com/watch?v=Z_S0VA4jKes&t=3s"
    ]
    
    chunks = processor.process_videos(video_urls)
    print(f"\nProcessed {len(chunks)} total chunks")
    if chunks:
        print(f"Sample chunk:\n{chunks[0]['text'][:200]}...")
