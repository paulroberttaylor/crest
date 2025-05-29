#!/usr/bin/env python3
"""
Quick Search Interface for Indexed Emails
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
    
    def search(self, query: str, n_results: int = 10):
        """Search emails and display results."""
        print(f"\nSearching for: '{query}'")
        print("-" * 80)
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['ids'][0]:
            print("No results found.")
            return
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            score = 1 - distance
            print(f"\nResult {i+1} (score: {score:.3f}):")
            print(f"Date: {metadata.get('date', 'Unknown')}")
            print(f"From: {metadata.get('from', 'Unknown')}")
            print(f"Subject: {metadata.get('subject', 'Unknown')}")
            
            # Show excerpt
            lines = document.split('\n')
            query_lower = query.lower()
            
            # Find most relevant part
            best_excerpt = ""
            for j, line in enumerate(lines[4:], 4):  # Skip headers
                if query_lower in line.lower() or any(word in line.lower() for word in query_lower.split()):
                    start = max(0, j-1)
                    end = min(len(lines), j+3)
                    best_excerpt = '\n'.join(lines[start:end])
                    break
            
            if not best_excerpt and len(lines) > 4:
                best_excerpt = '\n'.join(lines[4:8])
            
            if best_excerpt:
                print(f"Excerpt:\n{best_excerpt[:300]}...")
            
            print("-" * 40)
    
    def search_date_range(self, query: str, start_date: str, end_date: str):
        """Search within date range."""
        print(f"\nSearching for '{query}' between {start_date} and {end_date}")
        results = self.collection.query(
            query_texts=[query],
            n_results=50  # Get more results to filter
        )
        
        filtered = 0
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            date_str = metadata.get('date', '')
            if start_date <= date_str <= end_date:
                filtered += 1
                if filtered <= 10:  # Show first 10
                    print(f"\n{date_str[:10]} - {metadata.get('subject', 'Unknown')}")
                    print(f"From: {metadata.get('from', 'Unknown')}")
                    
        print(f"\nFound {filtered} results in date range")

def main():
    searcher = EmailSearcher()
    
    print("\nEmail Search Interface")
    print("=====================")
    print("Examples:")
    print("  plot 34 contract delay")
    print("  urgent exchange")
    print("  air brick buried")
    print("  completion december 2023")
    print("\nType 'quit' to exit\n")
    
    while True:
        query = input("Search: ").strip()
        
        if query.lower() == 'quit':
            break
        
        if query:
            searcher.search(query)

if __name__ == "__main__":
    main()