# NotebookLM-Style Study Tool

An interactive AI-powered study tool inspired by NotebookLM, designed for economics education with RAG-based Q&A, dialogue tutoring, and video-style summaries.

## Features

### 1. Q&A Mode
- Ask questions about the economics chapter
- Get answers grounded only in provided PDF and YouTube transcripts
- Cite sources for all responses

### 2. Dialogue Tutor Mode
- Interactive two-person dialogue (Student/Teacher)
- Step-by-step concept clarification
- Conversational learning experience

### 3. Video Summary Mode
- Structured chapter overview
- Key concepts and definitions
- Visual descriptions and exam tips
- Slide-style presentation format

## Setup Instructions

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Initial Data Ingestion
```bash
python ingestion/ingest_data.py
```

### 4. Launch the Application
```bash
streamlit run app.py
```

## Architecture

- **Data Ingestion**: Extracts and chunks PDF and YouTube transcripts
- **Embeddings**: Uses OpenAI embeddings with FAISS vector store
- **RAG System**: Retrieval-augmented generation for grounded responses
- **UI**: Streamlit-based interface with three distinct modes

## Data Sources

- Economics PDF (Chapter content)
- YouTube Video 1: Economics Tutorial
- YouTube Video 2: Concept Explanation

## Project Structure

```
notebooklm-study-tool/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── ingestion/
│   ├── pdf_processor.py   # PDF extraction and chunking
│   ├── youtube_processor.py # YouTube transcript extraction
│   └── ingest_data.py     # Main ingestion pipeline
├── rag/
│   ├── vector_store.py    # FAISS vector database
│   ├── embeddings.py      # Embedding generation
│   └── retriever.py       # RAG retrieval logic
├── modes/
│   ├── qa_mode.py         # Q&A functionality
│   ├── dialogue_mode.py   # Dialogue tutor
│   └── video_summary_mode.py # Video summary generation
└── data/
    ├── downloads/          # Downloaded source files
    └── processed/          # Processed chunks
```

## Notes

- This is a completely standalone system
- No dependencies on any existing PDF Q&A projects
- All data processing and storage is local
- Responses are strictly grounded in provided sources
