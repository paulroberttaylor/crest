#!/usr/bin/env python3
"""
Search for emails by date range and show all content
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
    
    def get_all_emails_in_date_range(self, start_date: str, end_date: str, max_results: int = 1000):
        """Get all emails in a date range."""
        print(f"\nGetting all emails between {start_date} and {end_date}...")
        
        # We'll use a generic query and then filter by date
        results = self.collection.query(
            query_texts=["email"],  # Generic query
            n_results=max_results
        )
        
        count = 0
        mortgage_count = 0
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            date_str = metadata.get('date', '')
            if start_date <= date_str <= end_date:
                count += 1
                
                # Check if this email mentions mortgage-related terms
                doc_lower = document.lower()
                mortgage_keywords = ['mortgage', 'interest rate', 'broker', 'lender', 'loan', 
                                   'mortgage offer', 'mortgage application', 'mortgage approval',
                                   'halifax', 'santander', 'nationwide', 'barclays', 'hsbc',
                                   'mortgage workshop', 'leanne athill', 'decision in principle',
                                   'mortgage in principle', 'rate', 'fixed rate', 'variable rate']
                
                if any(keyword in doc_lower for keyword in mortgage_keywords):
                    mortgage_count += 1
                    print(f"\n{'='*80}")
                    print(f"MORTGAGE-RELATED EMAIL #{mortgage_count}")
                    print(f"{'='*80}")
                    print(f"Date: {date_str}")
                    print(f"From: {metadata.get('from', 'Unknown')}")
                    print(f"To: {metadata.get('to', 'Unknown')}")
                    print(f"Subject: {metadata.get('subject', 'Unknown')}")
                    print(f"\nFull Email Content:")
                    print("-" * 40)
                    print(document)
                    print("-" * 80)
        
        print(f"\nTotal emails in date range: {count}")
        print(f"Mortgage-related emails found: {mortgage_count}")

def main():
    searcher = EmailSearcher()
    
    # Search for emails from Jan-May 2023
    searcher.get_all_emails_in_date_range("2023-01-01", "2023-05-31")

if __name__ == "__main__":
    main()