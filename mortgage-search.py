#!/usr/bin/env python3
"""
Search emails for mortgage-related information
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
    
    def search(self, query: str, n_results: int = 15):
        """Search emails and display results."""
        print(f"\n{'='*80}")
        print(f"Searching for: '{query}'")
        print(f"{'='*80}")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['ids'][0]:
            print("No results found.")
            return []
        
        found_emails = []
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            score = 1 - distance
            date_str = metadata.get('date', 'Unknown')
            
            # Only show emails from 2023 onwards
            if date_str >= '2023-01-01':
                print(f"\nResult {i+1} (relevance: {score:.3f}):")
                print(f"Date: {date_str}")
                print(f"From: {metadata.get('from', 'Unknown')}")
                print(f"To: {metadata.get('to', 'Unknown')}")
                print(f"Subject: {metadata.get('subject', 'Unknown')}")
                
                # Show more lines for context
                lines = document.split('\n')
                query_lower = query.lower()
                
                # Find most relevant part
                best_excerpt = ""
                excerpt_lines = []
                
                for j, line in enumerate(lines[4:], 4):  # Skip headers
                    if any(term in line.lower() for term in query_lower.split()) or \
                       '1.5%' in line or '1.5 percent' in line.lower():
                        start = max(4, j-3)
                        end = min(len(lines), j+4)
                        excerpt_lines = lines[start:end]
                        best_excerpt = '\n'.join(excerpt_lines)
                        break
                
                if not best_excerpt and len(lines) > 4:
                    best_excerpt = '\n'.join(lines[4:12])
                
                if best_excerpt:
                    print(f"\nContent excerpt:")
                    print("-" * 40)
                    print(best_excerpt[:500])
                    if len(best_excerpt) > 500:
                        print("...")
                
                found_emails.append({
                    'date': date_str,
                    'from': metadata.get('from', 'Unknown'),
                    'to': metadata.get('to', 'Unknown'),
                    'subject': metadata.get('subject', 'Unknown'),
                    'score': score,
                    'excerpt': best_excerpt
                })
                
                print("-" * 80)
        
        return found_emails

def main():
    searcher = EmailSearcher()
    
    print("\nSearching for mortgage-related emails...")
    print("Focus: 2023 onwards\n")
    
    # Search queries
    queries = [
        "mortgage in principle 1.5%",
        "mortgage principle rate",
        "1.5% mortgage offer",
        "mortgage advisor completion delay",
        "mortgage offer expired",
        "mortgage rate increase delay",
        "completion date mortgage impact",
        "mortgage broker Crest delay"
    ]
    
    all_results = []
    
    for query in queries:
        results = searcher.search(query, n_results=10)
        all_results.extend(results)
    
    # Additional targeted searches
    print(f"\n{'='*80}")
    print("Additional targeted search: mortgage + completion delays")
    print(f"{'='*80}")
    
    results = searcher.search("mortgage completion pushed back delayed", n_results=15)
    all_results.extend(results)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY OF MORTGAGE-RELATED EMAILS FOUND")
    print(f"{'='*80}")
    
    # Deduplicate by subject and date
    seen = set()
    unique_results = []
    for result in all_results:
        key = (result['date'], result['subject'])
        if key not in seen:
            seen.add(key)
            unique_results.append(result)
    
    # Sort by date
    unique_results.sort(key=lambda x: x['date'])
    
    print(f"\nTotal unique emails found: {len(unique_results)}")
    print("\nChronological list:")
    for result in unique_results:
        print(f"\n{result['date']} - {result['subject']}")
        print(f"From: {result['from']}")
        if '1.5' in str(result['excerpt']) or 'mortgage' in str(result['excerpt']).lower():
            print("*** Contains mortgage/rate information ***")

if __name__ == "__main__":
    main()