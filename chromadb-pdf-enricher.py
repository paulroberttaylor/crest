#!/usr/bin/env python3
"""
PDF Content Enricher for ChromaDB
Adds PDF content to already-indexed emails
"""

import os
import sys
import json
import chromadb
from chromadb.utils import embedding_functions
import pdfplumber
from PyPDF2 import PdfReader
import re
from typing import List, Dict
import time

class PDFEnricher:
    def __init__(self):
        # Connect to existing ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails")
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Get existing collection
        try:
            self.collection = self.client.get_collection(
                name="crest_emails",
                embedding_function=self.embedding_function
            )
            print(f"Connected to collection with {self.collection.count()} documents")
        except:
            print("Error: No email collection found. Run batch indexer first.")
            sys.exit(1)
        
        self.pdf_dir = "pdf_attachments"
        self.processed_pdfs = set()
    
    def extract_pdf_text(self, pdf_path: str, max_pages: int = 10) -> str:
        """Extract text from PDF."""
        text_content = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages[:max_pages]):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                    except:
                        continue
                        
                if len(pdf.pages) > max_pages:
                    text_content.append(f"\n[PDF has {len(pdf.pages)} pages, extracted first {max_pages}]")
        except Exception as e:
            print(f"  Failed to extract {os.path.basename(pdf_path)}: {e}")
            return ""
        
        return '\n'.join(text_content)[:20000]  # 20k char limit
    
    def find_important_pdfs(self) -> List[str]:
        """Find PDFs from Crest that are likely to be important."""
        important_pdfs = []
        
        # Focus on Crest PDFs
        crest_dir = os.path.join(self.pdf_dir, "crestnicholson.com")
        if os.path.exists(crest_dir):
            for filename in os.listdir(crest_dir):
                if filename.endswith('.pdf'):
                    # Prioritize certain types
                    if any(keyword in filename.lower() for keyword in 
                           ['complaint', 'response', 'assessment', 'pathway', 'resolution', 'settlement']):
                        important_pdfs.append(os.path.join(crest_dir, filename))
        
        # Also check NHOS PDFs
        nhos_dir = os.path.join(self.pdf_dir, "nhos.org.uk")
        if os.path.exists(nhos_dir):
            for filename in os.listdir(nhos_dir):
                if filename.endswith('.pdf'):
                    important_pdfs.append(os.path.join(nhos_dir, filename))
        
        return important_pdfs
    
    def enrich_emails_with_pdfs(self):
        """Add PDF content to emails that reference them."""
        print("Finding important PDFs to index...")
        important_pdfs = self.find_important_pdfs()
        print(f"Found {len(important_pdfs)} important PDFs")
        
        # Process each PDF
        for i, pdf_path in enumerate(important_pdfs):
            if i % 10 == 0:
                print(f"\nProcessing PDF {i+1}/{len(important_pdfs)}...")
            
            filename = os.path.basename(pdf_path)
            print(f"  Extracting: {filename}")
            
            # Extract PDF text
            pdf_text = self.extract_pdf_text(pdf_path)
            if not pdf_text:
                continue
            
            # Search for emails that mention this PDF
            results = self.collection.query(
                query_texts=[filename],
                n_results=5,
                where={"has_pdf": True}
            )
            
            if results['ids'][0]:
                print(f"  Found {len(results['ids'][0])} emails referencing this PDF")
                
                # Update each email with PDF content
                for email_id, metadata, document in zip(
                    results['ids'][0], 
                    results['metadatas'][0], 
                    results['documents'][0]
                ):
                    # Check if already has PDF content
                    if "[PDF CONTENT]" not in document:
                        # Create enriched document
                        enriched_doc = document + f"\n\n[PDF CONTENT: {filename}]\n{pdf_text[:5000]}"
                        
                        # Update in collection
                        try:
                            self.collection.update(
                                ids=[email_id],
                                documents=[enriched_doc],
                                metadatas=[metadata]
                            )
                        except:
                            # If update fails, skip
                            pass
            
            # Save memory
            if i % 20 == 0:
                time.sleep(0.5)  # Brief pause
        
        print(f"\nPDF enrichment complete!")

def main():
    enricher = PDFEnricher()
    
    try:
        enricher.enrich_emails_with_pdfs()
    except KeyboardInterrupt:
        print("\nEnrichment interrupted!")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()