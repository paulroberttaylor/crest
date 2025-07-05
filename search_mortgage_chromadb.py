#!/usr/bin/env python3
"""Search ChromaDB for mortgage-related content"""

import chromadb
from chromadb.utils import embedding_functions

def search_mortgage_content():
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path="./chromadb_emails_quick")
    
    # Get embedding function
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # Get the collection
    collection = client.get_collection(
        name="emails",
        embedding_function=embedding_fn
    )
    
    # Search queries
    queries = [
        "mortgage broker fee payment £1495",
        "The Mortgage Workshop",
        "mortgage advisor broker",
        "mortgage arrangement fee",
        "mortgage interest rate percentage",
        "mortgage application delay"
    ]
    
    print("=== CHROMADB MORTGAGE SEARCH RESULTS ===\n")
    
    all_results = []
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        print("-" * 60)
        
        results = collection.query(
            query_texts=[query],
            n_results=5,
            include=["metadatas", "distances", "documents"]
        )
        
        if results['ids'][0]:
            for i, (id, metadata, distance, doc) in enumerate(zip(
                results['ids'][0],
                results['metadatas'][0],
                results['distances'][0],
                results['documents'][0]
            )):
                if distance < 1.2:  # Only show relevant results
                    print(f"\n  Result {i+1} (relevance: {1-distance:.2%}):")
                    print(f"  Date: {metadata.get('date', 'Unknown')}")
                    print(f"  Subject: {metadata.get('subject', 'No subject')}")
                    print(f"  From: {metadata.get('from', 'Unknown')}")
                    print(f"  Preview: {doc[:200]}...")
                    
                    # Store for deduplication
                    all_results.append({
                        'id': id,
                        'metadata': metadata,
                        'distance': distance,
                        'doc': doc,
                        'query': query
                    })
    
    # Deduplicate and show unique mortgage-related emails
    unique_emails = {}
    for result in all_results:
        email_id = result['metadata'].get('date', '') + result['metadata'].get('subject', '')
        if email_id not in unique_emails or result['distance'] < unique_emails[email_id]['distance']:
            unique_emails[email_id] = result
    
    print("\n\n=== UNIQUE MORTGAGE-RELATED EMAILS ===")
    print(f"Found {len(unique_emails)} unique mortgage-related emails\n")
    
    for email_id, result in sorted(unique_emails.items(), key=lambda x: x[1]['metadata'].get('date', '')):
        print(f"\nDate: {result['metadata'].get('date', 'Unknown')}")
        print(f"Subject: {result['metadata'].get('subject', 'No subject')}")
        print(f"From: {result['metadata'].get('from', 'Unknown')}")
        print(f"To: {result['metadata'].get('to', 'Unknown')}")
        print(f"Best match for: '{result['query']}'")
        print(f"Relevance: {1-result['distance']:.2%}")
        
        # Show relevant content excerpt
        doc_lower = result['doc'].lower()
        if 'mortgage' in doc_lower:
            start = max(0, doc_lower.find('mortgage') - 100)
            end = min(len(result['doc']), doc_lower.find('mortgage') + 200)
            print(f"Context: ...{result['doc'][start:end]}...")

if __name__ == "__main__":
    search_mortgage_content()