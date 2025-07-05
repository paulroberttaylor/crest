#!/usr/bin/env python3
"""
Check the date range of indexed emails
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
    
    def check_date_range(self):
        """Check the date range of all emails."""
        print("\nChecking date range of indexed emails...")
        
        # Get a large sample of emails
        results = self.collection.query(
            query_texts=["email"],
            n_results=1000
        )
        
        dates = []
        for metadata in results['metadatas'][0]:
            date_str = metadata.get('date', '')
            if date_str:
                dates.append(date_str)
        
        if dates:
            dates.sort()
            print(f"\nEarliest email: {dates[0]}")
            print(f"Latest email: {dates[-1]}")
            
            # Count emails by year
            year_counts = {}
            for date in dates:
                year = date[:4]
                year_counts[year] = year_counts.get(year, 0) + 1
            
            print("\nEmails by year:")
            for year in sorted(year_counts.keys()):
                print(f"  {year}: {year_counts[year]} emails")
            
            # Count 2023 emails by month
            print("\n2023 emails by month:")
            month_counts = {}
            for date in dates:
                if date.startswith('2023'):
                    month = date[:7]
                    month_counts[month] = month_counts.get(month, 0) + 1
            
            for month in sorted(month_counts.keys()):
                print(f"  {month}: {month_counts[month]} emails")

def main():
    searcher = EmailSearcher()
    searcher.check_date_range()

if __name__ == "__main__":
    main()