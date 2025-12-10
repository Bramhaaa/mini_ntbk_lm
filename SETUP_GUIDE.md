# Setup Guide - NotebookLM Study Tool

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git
- Internet connection (for initial data download)

## Step-by-Step Setup

### 1. Environment Setup

```bash
# Navigate to project directory
cd notebooklm-study-tool

# Run the setup script (macOS/Linux)
./setup.sh

# OR manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Open .env in your editor and set:
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run Data Ingestion

This step downloads the PDF and extracts YouTube transcripts:

```bash
python ingestion/ingest_data.py
```

**Expected Output:**
```
==================================================
STEP 1: Processing Economics PDF
==================================================
✓ Downloaded PDF to: data/downloads/economics_chapter.pdf
✓ Extracted text from [X] pages
✓ Created [X] chunks from PDF

==================================================
STEP 2: Processing YouTube Videos
==================================================
✓ Extracted transcript from video [ID]
✓ Created [X] chunks from video transcript
...
✓ Total chunks from all videos: [X]

==================================================
INGESTION COMPLETE
==================================================
✓ Total chunks processed: [X]
✓ Saved to: data/processed/all_chunks.json
```

### 4. Build Vector Store

Generate embeddings and create the FAISS index:

```bash
python build_vector_store.py
```

**Expected Output:**
```
==================================================
BUILDING VECTOR STORE
==================================================
✓ Loaded [X] chunks
Generating embeddings for [X] chunks...
  Processing batch 1/[X]
  ...
✓ Generated [X] embeddings
Creating FAISS index...
✓ Added [X] vectors to index
✓ Saved vector store to: data/vector_store
```

### 5. Launch the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution:** Make sure you created the `.env` file and added your API key.

### Issue: "Vector store not found"
**Solution:** Run `python build_vector_store.py` before launching the app.

### Issue: "Chunks file not found"
**Solution:** Run `python ingestion/ingest_data.py` first.

### Issue: YouTube transcript extraction fails
**Solution:** 
- Check internet connection
- Some videos may not have transcripts available
- The system will continue with available transcripts

### Issue: PDF download fails
**Solution:**
- Verify the Google Drive link is accessible
- Check internet connection
- Manually download and place in `data/downloads/`

## Project Structure

```
notebooklm-study-tool/
├── app.py                      # Main Streamlit application
├── build_vector_store.py       # Embedding generation script
├── setup.sh                    # Setup script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example               # Example environment file
├── README.md                   # Project documentation
├── SETUP_GUIDE.md             # This file
├── ingestion/
│   ├── pdf_processor.py       # PDF extraction
│   ├── youtube_processor.py   # YouTube transcript extraction
│   └── ingest_data.py         # Main ingestion pipeline
├── rag/
│   ├── embeddings.py          # OpenAI embeddings
│   ├── vector_store.py        # FAISS vector database
│   └── retriever.py           # RAG retrieval logic
├── modes/
│   ├── qa_mode.py             # Q&A functionality
│   ├── dialogue_mode.py       # Dialogue tutor
│   └── video_summary_mode.py  # Video summaries
└── data/
    ├── downloads/              # Downloaded source files
    ├── processed/              # Processed chunks
    └── vector_store/           # FAISS index and metadata
```

## Testing Individual Components

### Test PDF Processor
```bash
cd ingestion
python pdf_processor.py
```

### Test YouTube Processor
```bash
cd ingestion
python youtube_processor.py
```

### Test Embeddings
```bash
cd rag
python embeddings.py
```

### Test Vector Store
```bash
cd rag
python vector_store.py
```

## Usage

Once the application is running:

1. **Q&A Mode**: Ask questions about the economics chapter
2. **Dialogue Tutor**: Generate Student-Teacher conversations
3. **Video Summary**: Create structured chapter overviews

All responses are grounded in the provided PDF and YouTube transcripts.

## Notes

- First-time setup takes 5-10 minutes depending on your internet speed
- Embedding generation uses OpenAI API and will incur costs (typically <$1 for this dataset)
- The vector store is saved locally and doesn't need to be rebuilt unless data changes
- All data processing is local except for API calls to OpenAI

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure API key is valid and has sufficient credits
4. Check terminal output for specific error messages
