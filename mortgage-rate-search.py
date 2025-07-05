#!/usr/bin/env python3
"""
Search for specific mortgage rate information in emails
"""

import chromadb
from chromadb.utils import embedding_functions
import sys
import re

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
            print(f"Connected to {self.collection.count()} indexed emails\n")
        except:
            print("Error: No indexed emails found.")
            sys.exit(1)
    
    def search_and_analyze(self, query: str, n_results: int = 50):
        """Search emails and analyze for mortgage rate info."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['ids'][0]:
            return []
        
        found_emails = []
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            date_str = metadata.get('date', 'Unknown')
            
            # Only process emails from 2023 onwards
            if date_str >= '2023-01-01':
                # Look for rate mentions
                rate_pattern = r'\b(\d+\.?\d*)%|\b(\d+\.?\d*)\s*percent'
                mortgage_terms = ['mortgage', 'rate', 'interest', 'offer', 'broker', 'advisor']
                
                content_lower = document.lower()
                has_mortgage_context = any(term in content_lower for term in mortgage_terms)
                rate_matches = re.findall(rate_pattern, document, re.IGNORECASE)
                
                if has_mortgage_context or rate_matches:
                    found_emails.append({
                        'date': date_str,
                        'from': metadata.get('from', 'Unknown'),
                        'to': metadata.get('to', 'Unknown'),
                        'subject': metadata.get('subject', 'Unknown'),
                        'document': document,
                        'rate_matches': rate_matches,
                        'has_mortgage_context': has_mortgage_context
                    })
        
        return found_emails

def main():
    searcher = EmailSearcher()
    
    print("Searching for mortgage rate information in emails...\n")
    
    # Multiple search strategies
    all_results = []
    
    # Search for direct rate mentions
    queries = [
        "1.5% rate mortgage",
        "mortgage rate increased",
        "lost mortgage rate delay",
        "mortgage advisor rate change",
        "interest rate mortgage Crest delay",
        "mortgage offer June July 2023",
        "mortgage product term rate"
    ]
    
    for query in queries:
        print(f"Searching: {query}")
        results = searcher.search_and_analyze(query, n_results=30)
        all_results.extend(results)
    
    # Deduplicate
    seen = set()
    unique_results = []
    for result in all_results:
        key = (result['date'], result['subject'])
        if key not in seen:
            seen.add(key)
            unique_results.append(result)
    
    # Sort by date
    unique_results.sort(key=lambda x: x['date'])
    
    print(f"\n{'='*80}")
    print("EMAILS WITH MORTGAGE RATE INFORMATION")
    print(f"{'='*80}\n")
    
    # Display results with rate context
    for result in unique_results:
        if result['rate_matches'] or '1.5' in result['document']:
            print(f"\nDate: {result['date']}")
            print(f"From: {result['from']}")
            print(f"Subject: {result['subject']}")
            
            # Extract relevant context
            lines = result['document'].split('\n')
            for i, line in enumerate(lines):
                if '1.5' in line or any(match[0] or match[1] for match in result['rate_matches'] if match[0] in line or match[1] in line):
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    context = '\n'.join(lines[start:end])
                    print(f"\nRate mention context:")
                    print("-" * 40)
                    print(context)
                    break
            
            print("=" * 80)
    
    # Look for specific June/July 2023 mortgage discussions
    print(f"\n{'='*80}")
    print("JUNE-JULY 2023 MORTGAGE DISCUSSIONS")
    print(f"{'='*80}\n")
    
    june_july_emails = [r for r in unique_results if '2023-06' in r['date'] or '2023-07' in r['date']]
    
    for result in june_july_emails:
        if 'mortgage' in result['document'].lower() or 'rate' in result['document'].lower():
            print(f"\nDate: {result['date']}")
            print(f"Subject: {result['subject']}")
            
            # Show mortgage-related excerpts
            lines = result['document'].split('\n')
            for i, line in enumerate(lines):
                if 'mortgage' in line.lower() or 'rate' in line.lower() or 'advisor' in line.lower():
                    start = max(0, i-1)
                    end = min(len(lines), i+2)
                    excerpt = '\n'.join(lines[start:end])
                    print(f"\nExcerpt:")
                    print(excerpt[:300])
                    break

if __name__ == "__main__":
    main()