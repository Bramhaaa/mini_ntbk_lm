#!/bin/bash

# Setup script for NotebookLM Study Tool

echo "=========================================="
echo "NotebookLM Study Tool - Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create .env file and add your OPENAI_API_KEY:"
echo "   cp .env.example .env"
echo "   # Edit .env and add your API key"
echo ""
echo "2. Run data ingestion:"
echo "   python ingestion/ingest_data.py"
echo ""
echo "3. Build vector store:"
echo "   python build_vector_store.py"
echo ""
echo "4. Launch the application:"
echo "   streamlit run app.py"
echo ""
echo "=========================================="
