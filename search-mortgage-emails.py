#!/usr/bin/env python3
"""
Search for mortgage-related emails from early 2023
"""

import chromadb
from chromadb.utils import embedding_functions
import sys
from datetime import datetime

class EmailSearcher:
    def __init__(self):
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails_quick")
        
        # Use same embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get collection
        try:
            self.collection = self.client.get_collection(
                name="emails_quick",
                embedding_function=self.embedding_function
            )
            print(f"Connected to {self.collection.count()} indexed emails")
        except:
            print("Error: No indexed emails found. Run quick-indexer.py first.")
            sys.exit(1)
    
    def search_and_print(self, query: str, n_results: int = 20):
        """Search emails and display results."""
        print(f"\n{'='*80}")
        print(f"Searching for: '{query}'")
        print(f"{'='*80}\n")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['ids'][0]:
            print("No results found.")
            return
        
        # Filter for 2023 emails only
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            date_str = metadata.get('date', '')
            # Only show 2023 emails
            if date_str.startswith('2023'):
                score = 1 - distance
                print(f"\nResult {i+1} (score: {score:.3f}):")
                print(f"Date: {date_str}")
                print(f"From: {metadata.get('from', 'Unknown')}")
                print(f"To: {metadata.get('to', 'Unknown')}")
                print(f"Subject: {metadata.get('subject', 'Unknown')}")
                print(f"\nFull Email Content:")
                print("-" * 40)
                print(document[:2000])  # Show first 2000 chars
                if len(document) > 2000:
                    print(f"\n[... {len(document) - 2000} more characters ...]")
                print("-" * 80)

def main():
    searcher = EmailSearcher()
    
    # Search queries for mortgage-related emails
    queries = [
        "mortgage rate offer 2023",
        "Leanne Athill mortgageworkshop",
        "mortgage in principle plot 34",
        "decision in principle colt view",
        "1.5% mortgage rate",
        "2% mortgage rate", 
        "mortgage offer expired",
        "mortgage broker plot 34"
    ]
    
    print("\nSearching for mortgage-related emails from 2023...")
    
    for query in queries:
        searcher.search_and_print(query)

if __name__ == "__main__":
    main()