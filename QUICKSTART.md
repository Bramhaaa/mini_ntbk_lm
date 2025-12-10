# 🚀 Quick Start Guide

## Immediate Next Steps

### 1. Configure Your API Key (2 minutes)

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file and add your OpenAI API key
# Replace 'your_openai_api_key_here' with your actual key
```

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

### 2. Install Dependencies (2-3 minutes)

```bash
# Run the automated setup script
./setup.sh

# OR manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Ingest Data (3-5 minutes)

This downloads the PDF and extracts YouTube transcripts:

```bash
# Activate virtual environment first (if not already)
source venv/bin/activate

# Run ingestion
python ingestion/ingest_data.py
```

### 4. Build Vector Store (2-3 minutes)

Generate embeddings and create searchable index:

```bash
python build_vector_store.py
```

💰 **Note**: This step uses OpenAI API and typically costs less than $1

### 5. Launch the App! (30 seconds)

```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

---

## What You'll See

### 💬 Q&A Mode
- Ask any question about the economics chapter
- Get answers grounded in PDF + videos
- See source citations

### 🎭 Dialogue Tutor Mode
- Generate Student-Teacher conversations
- Step-by-step concept explanations
- Perfect for understanding complex topics

### 🎥 Video Summary Mode
- Structured chapter overviews
- Key concepts and definitions
- Exam tips and revision points
- Downloadable summaries

---

## Total Setup Time: ~10-15 minutes

## Troubleshooting

**App won't start?**
- Make sure you ran all 5 steps above
- Check that `.env` has your API key
- Verify vector store was built successfully

**Need help?** Check `SETUP_GUIDE.md` for detailed troubleshooting

---

## Architecture Overview

```
Your Question → Vector Search → Retrieve Relevant Chunks → 
Generate Answer with GPT-4 → Display with Sources
```

**All responses are grounded in:**
- ✅ Economics PDF chapter
- ✅ YouTube video transcripts
- ❌ No external/hallucinated information

---

## Project is 100% Standalone

✅ New codebase
✅ New database
✅ New embeddings
✅ No shared dependencies with any other project
✅ Complete separation from existing systems

Happy studying! 📚
