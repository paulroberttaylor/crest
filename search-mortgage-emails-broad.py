#!/usr/bin/env python3
"""
Broader search for mortgage-related emails from early 2023
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
    
    def search_and_print(self, query: str, n_results: int = 30):
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
        
        count = 0
        # Filter for early 2023 emails only (Jan-May)
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            date_str = metadata.get('date', '')
            # Only show early 2023 emails
            if (date_str.startswith('2023-01') or date_str.startswith('2023-02') or 
                date_str.startswith('2023-03') or date_str.startswith('2023-04') or 
                date_str.startswith('2023-05')):
                count += 1
                score = 1 - distance
                print(f"\nResult {count} (score: {score:.3f}):")
                print(f"Date: {date_str}")
                print(f"From: {metadata.get('from', 'Unknown')}")
                print(f"To: {metadata.get('to', 'Unknown')}")
                print(f"Subject: {metadata.get('subject', 'Unknown')}")
                print(f"\nEmail Preview:")
                print("-" * 40)
                # Show content, looking for mortgage-related keywords
                content_preview = document[:1500]
                print(content_preview)
                if len(document) > 1500:
                    print(f"\n[... {len(document) - 1500} more characters ...]")
                print("-" * 80)
        
        if count == 0:
            print(f"No results found from Jan-May 2023 for query: {query}")

def main():
    searcher = EmailSearcher()
    
    # Broader search queries
    queries = [
        "mortgage",
        "Leanne Athill",
        "mortgageworkshop",
        "interest rate",
        "mortgage offer",
        "mortgage broker",
        "Halifax mortgage",
        "Santander mortgage",
        "mortgage application",
        "mortgage approval"
    ]
    
    print("\nSearching for mortgage-related emails from Jan-May 2023...")
    
    for query in queries:
        searcher.search_and_print(query)

if __name__ == "__main__":
    main()