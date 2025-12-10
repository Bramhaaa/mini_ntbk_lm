"""
PDF Processor Module
Handles downloading and processing of PDF documents for the study tool.
Supports both text-based PDFs and scanned PDFs using OCR.
"""

import os
import requests
import pypdf
from typing import List, Dict
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image


class PDFProcessor:
    """Process PDF documents from Google Drive links."""
    
    def __init__(self, output_dir: str = "data/downloads"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def download_from_drive(self, drive_url: str, filename: str) -> str:
        """
        Download PDF from Google Drive sharing link.
        
        Args:
            drive_url: Google Drive sharing URL
            filename: Output filename
            
        Returns:
            Path to downloaded file
        """
        # Extract file ID from Google Drive URL
        file_id = self._extract_file_id(drive_url)
        
        # Direct download URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Download with session to handle large files
        session = requests.Session()
        response = session.get(download_url, stream=True)
        
        # Check for download confirmation (large files)
        if 'download_warning' in response.cookies:
            params = {'confirm': response.cookies['download_warning']}
            response = session.get(download_url, params=params, stream=True)
        
        # Save file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
        
        print(f"✓ Downloaded PDF to: {output_path}")
        return output_path
    
    def _extract_file_id(self, drive_url: str) -> str:
        """Extract file ID from various Google Drive URL formats."""
        patterns = [
            r'/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, drive_url)
            if match:
                return match.group(1)
        
        raise ValueError("Could not extract file ID from Google Drive URL")
    
    def extract_text(self, pdf_path: str, use_ocr: bool = True) -> str:
        """
        Extract all text from PDF, with OCR fallback for scanned PDFs.
        
        Args:
            pdf_path: Path to PDF file
            use_ocr: Use OCR for scanned PDFs
            
        Returns:
            Extracted text content
        """
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ""
            total_pages = len(reader.pages)
            
            print(f"Processing {total_pages} pages...")
            
            # First try regular text extraction
            for page_num in range(total_pages):
                try:
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                except Exception as e:
                    print(f"  Warning: Could not extract text from page {page_num + 1}: {e}")
            
            # If no text extracted and OCR is enabled, use OCR
            if len(text.strip()) < 100 and use_ocr:
                print("⚠ Little or no text extracted. Using OCR to read scanned PDF...")
                text = self._extract_text_with_ocr(pdf_path)
            else:
                print(f"✓ Extracted text from {total_pages} pages")
            
            return text
    
    def _extract_text_with_ocr(self, pdf_path: str) -> str:
        """
        Extract text from scanned PDF using OCR.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            OCR extracted text
        """
        print("  Converting PDF to images...")
        images = convert_from_path(pdf_path)
        
        text = ""
        total_pages = len(images)
        
        print(f"  Running OCR on {total_pages} pages...")
        for page_num, image in enumerate(images, 1):
            try:
                # Run OCR on the image
                page_text = pytesseract.image_to_string(image)
                if page_text.strip():
                    text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                print(f"    ✓ OCR page {page_num}/{total_pages}")
            except Exception as e:
                print(f"    ✗ Error OCR page {page_num}: {e}")
        
        print(f"✓ Extracted text from {total_pages} pages using OCR")
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, str]]:
        """
        Split text into overlapping chunks for RAG.
        
        Args:
            text: Full text content
            chunk_size: Target size for each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Clean text
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or exclamation point
                period_pos = text.rfind('.', start, end)
                question_pos = text.rfind('?', start, end)
                exclaim_pos = text.rfind('!', start, end)
                
                best_pos = max(period_pos, question_pos, exclaim_pos)
                if best_pos > start:
                    end = best_pos + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'id': f'pdf_chunk_{chunk_id}',
                    'text': chunk_text,
                    'source': 'economics_pdf',
                    'type': 'pdf',
                    'chunk_index': chunk_id
                })
                chunk_id += 1
            
            start = end - overlap
        
        print(f"✓ Created {len(chunks)} chunks from PDF")
        return chunks
    
    def process_pdf(self, drive_url: str, filename: str = "economics_chapter.pdf") -> List[Dict[str, str]]:
        """
        Complete pipeline: download, extract, and chunk PDF.
        
        Args:
            drive_url: Google Drive sharing URL
            filename: Output filename
            
        Returns:
            List of text chunks with metadata
        """
        print(f"\n📄 Processing PDF...")
        pdf_path = self.download_from_drive(drive_url, filename)
        text = self.extract_text(pdf_path)
        chunks = self.chunk_text(text)
        
        return chunks


if __name__ == "__main__":
    # Test the processor
    processor = PDFProcessor()
    drive_url = "https://drive.google.com/file/d/1K9tjpEljoDnYXwW1y4jt_gxW1753lxBW/view?usp=drive_link"
    chunks = processor.process_pdf(drive_url)
    print(f"\nProcessed {len(chunks)} chunks")
    print(f"Sample chunk:\n{chunks[0]['text'][:200]}...")
