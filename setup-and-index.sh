#!/bin/bash
# Setup virtual environment and run ChromaDB indexer

echo "Creating virtual environment..."
python3 -m venv email_indexer_env

echo "Activating virtual environment..."
source email_indexer_env/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running email indexer..."
python chromadb-email-indexer.py Crest-NHOS-Export.mbox pdf_attachments

echo "Setup complete! To use the search interface later, run:"
echo "source email_indexer_env/bin/activate"
echo "python chromadb-email-indexer.py Crest-NHOS-Export.mbox pdf_attachments"