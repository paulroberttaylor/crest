#!/usr/bin/env python3
"""
ChromaDB Email Search Interface
Search previously indexed emails without re-indexing
"""

import chromadb
from chromadb.utils import embedding_functions
import json
import sys
from typing import Dict, Optional

class EmailSearcher:
    def __init__(self):
        # Connect to existing ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails")
        
        # Use the default embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Get existing collection
        try:
            self.collection = self.client.get_collection(
                name="crest_emails",
                embedding_function=self.embedding_function
            )
            print(f"Connected to email collection with {self.collection.count()} documents")
        except Exception as e:
            print(f"Error: Could not find email collection. Run chromadb-email-indexer.py first.")
            print(f"Details: {e}")
            sys.exit(1)
    
    def search(self, query: str, n_results: int = 10, filters: Optional[Dict] = None) -> Dict:
        """Search the email collection."""
        where_clause = filters if filters else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        return results
    
    def search_with_display(self, query: str, n_results: int = 10, filters: Optional[Dict] = None):
        """Search and display results in a readable format."""
        results = self.search(query, n_results, filters)
        
        if not results['ids'][0]:
            print("No results found.")
            return
        
        print(f"\nFound {len(results['ids'][0])} results for: '{query}'\n")
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            print(f"Result {i+1} (relevance score: {1-distance:.3f}):")
            print(f"Date: {metadata.get('date', 'Unknown')[:10]}")
            print(f"From: {metadata.get('from', 'Unknown')}")
            print(f"To: {metadata.get('to', 'Unknown')}")
            print(f"Subject: {metadata.get('subject', 'Unknown')}")
            
            if metadata.get('has_pdf'):
                pdf_files = json.loads(metadata.get('pdf_filenames', '[]'))
                print(f"PDF Attachments: {', '.join(pdf_files)}")
            
            # Show relevant excerpt
            query_lower = query.lower()
            doc_lower = document.lower()
            
            # Find best matching section
            best_start = 0
            if query_lower in doc_lower:
                best_start = doc_lower.find(query_lower)
            else:
                # Find section with most query words
                query_words = query_lower.split()
                best_score = 0
                for i in range(0, len(doc_lower), 100):
                    section = doc_lower[i:i+500]
                    score = sum(1 for word in query_words if word in section)
                    if score > best_score:
                        best_score = score
                        best_start = i
            
            excerpt_start = max(0, best_start - 200)
            excerpt_end = min(len(document), best_start + 500)
            excerpt = document[excerpt_start:excerpt_end]
            
            # Clean up excerpt
            excerpt = excerpt.replace('\n', ' ')
            excerpt = ' '.join(excerpt.split())
            
            if excerpt_start > 0:
                excerpt = "..." + excerpt
            if excerpt_end < len(document):
                excerpt = excerpt + "..."
            
            print(f"Excerpt: {excerpt}")
            print("-" * 80)
    
    def search_by_date_range(self, query: str, start_date: str, end_date: str, n_results: int = 20):
        """Search within a specific date range."""
        # Parse dates to extract year, month, day
        start_year, start_month, start_day = map(int, start_date.split('-'))
        end_year, end_month, end_day = map(int, end_date.split('-'))
        
        # ChromaDB doesn't support complex date filtering, so we'll get more results and filter
        results = self.search(query, n_results=50)
        
        filtered_results = {
            'ids': [[]],
            'metadatas': [[]],
            'documents': [[]],
            'distances': [[]]
        }
        
        for i, metadata in enumerate(results['metadatas'][0]):
            date_str = metadata.get('date', '')[:10]
            if start_date <= date_str <= end_date:
                filtered_results['ids'][0].append(results['ids'][0][i])
                filtered_results['metadatas'][0].append(metadata)
                filtered_results['documents'][0].append(results['documents'][0][i])
                filtered_results['distances'][0].append(results['distances'][0][i])
        
        return filtered_results
    
    def search_from_person(self, query: str, person: str, n_results: int = 10):
        """Search emails from a specific person."""
        filters = None
        
        if person.lower() == 'crest':
            filters = {"from_crest": True}
        elif person.lower() == 'paul':
            filters = {"from_paul": True}
        elif person.lower() == 'jade':
            filters = {"from_jade": True}
        elif person.lower() == 'nhos':
            filters = {"from_nhos": True}
        
        return self.search_with_display(query, n_results, filters)
    
    def search_with_pdfs(self, query: str, n_results: int = 10):
        """Search only emails that have PDF attachments."""
        filters = {"has_pdf": True}
        return self.search_with_display(query, n_results, filters)

def main():
    searcher = EmailSearcher()
    
    print("\n\nEmail Search Interface")
    print("======================")
    print("\nExample searches:")
    print("  - plot 34 contract delay")
    print("  - air brick buried") 
    print("  - render crack")
    print("  - completion december 2023")
    print("\nSpecial commands:")
    print("  - from:crest <query>     - Search emails from Crest")
    print("  - from:paul <query>      - Search emails from Paul")
    print("  - from:jade <query>      - Search emails from Jade")
    print("  - pdf: <query>           - Search only emails with PDFs")
    print("  - date:2023-10-01:2023-12-31 <query> - Search date range")
    print("\nType 'quit' to exit.\n")
    
    while True:
        query = input("Search query: ").strip()
        if query.lower() == 'quit':
            break
        
        if not query:
            continue
        
        # Parse special commands
        if query.startswith('from:'):
            parts = query.split(' ', 1)
            if len(parts) == 2:
                person = parts[0][5:]  # Remove 'from:'
                search_query = parts[1]
                searcher.search_from_person(search_query, person)
            else:
                print("Usage: from:<person> <search query>")
        
        elif query.startswith('pdf:'):
            search_query = query[4:].strip()
            searcher.search_with_pdfs(search_query)
        
        elif query.startswith('date:'):
            parts = query.split(' ', 1)
            if len(parts) == 2:
                date_part = parts[0][5:]  # Remove 'date:'
                if ':' in date_part:
                    start_date, end_date = date_part.split(':', 1)
                    search_query = parts[1]
                    results = searcher.search_by_date_range(search_query, start_date, end_date)
                    # Display filtered results
                    if not results['ids'][0]:
                        print("No results found in date range.")
                    else:
                        print(f"\nFound {len(results['ids'][0])} results in date range {start_date} to {end_date}\n")
                        for i, (doc_id, metadata, document, distance) in enumerate(zip(
                            results['ids'][0], 
                            results['metadatas'][0], 
                            results['documents'][0],
                            results['distances'][0]
                        )):
                            print(f"Result {i+1}:")
                            print(f"Date: {metadata.get('date', 'Unknown')[:10]}")
                            print(f"Subject: {metadata.get('subject', 'Unknown')}")
                            print(f"From: {metadata.get('from', 'Unknown')}")
                            print("-" * 40)
                else:
                    print("Usage: date:YYYY-MM-DD:YYYY-MM-DD <search query>")
            else:
                print("Usage: date:YYYY-MM-DD:YYYY-MM-DD <search query>")
        
        else:
            searcher.search_with_display(query)

if __name__ == "__main__":
    main()