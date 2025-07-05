#!/usr/bin/env python3
"""Search ChromaDB for evidence of mortgage extensions and second mortgage applications"""

import chromadb
from chromadb.utils import embedding_functions
import json

def search_mortgage_extensions():
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path="./chromadb_emails_quick")
    
    # Get embedding function
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # Get the collection
    collection = client.get_collection(
        name="emails",
        embedding_function=embedding_fn
    )
    
    # Search queries specifically for mortgage extensions and reapplications
    queries = [
        "mortgage offer expire expiry extension",
        "second mortgage application",
        "mortgage reapplication new application",
        "mortgage extension fee cost",
        "mortgage offer validity period",
        "mortgage broker extend extension",
        "The Mortgage Workshop extension",
        "mortgage offer running out",
        "mortgage deadline pressure",
        "mortgage offer 3 months 6 months",
        "had to reapply for mortgage",
        "mortgage application twice",
        "mortgage broker fee second time",
        "mortgage valuation second",
        "mortgage arrangement fee again"
    ]
    
    print("=== MORTGAGE EXTENSION/REAPPLICATION SEARCH ===\n")
    
    all_results = []
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        print("-" * 60)
        
        results = collection.query(
            query_texts=[query],
            n_results=10,
            include=["metadatas", "distances", "documents"]
        )
        
        if results['ids'][0]:
            for i, (id, metadata, distance, doc) in enumerate(zip(
                results['ids'][0],
                results['metadatas'][0],
                results['distances'][0],
                results['documents'][0]
            )):
                if distance < 1.3:  # Slightly higher threshold for broader matches
                    all_results.append({
                        'id': id,
                        'metadata': metadata,
                        'distance': distance,
                        'doc': doc,
                        'query': query,
                        'date': metadata.get('date', ''),
                        'subject': metadata.get('subject', '')
                    })
    
    # Deduplicate and sort by date
    unique_emails = {}
    for result in all_results:
        email_key = result['date'] + result['subject']
        if email_key not in unique_emails or result['distance'] < unique_emails[email_key]['distance']:
            unique_emails[email_key] = result
    
    # Sort by date
    sorted_results = sorted(unique_emails.values(), key=lambda x: x['date'])
    
    print("\n\n=== CHRONOLOGICAL MORTGAGE EXTENSION/REAPPLICATION EVIDENCE ===")
    print(f"Found {len(sorted_results)} potentially relevant emails\n")
    
    findings = {
        'mortgage_extension_evidence': [],
        'key_dates': [],
        'financial_impact': []
    }
    
    for result in sorted_results:
        print(f"\nDate: {result['metadata'].get('date', 'Unknown')}")
        print(f"Subject: {result['metadata'].get('subject', 'No subject')}")
        print(f"From: {result['metadata'].get('from', 'Unknown')}")
        print(f"To: {result['metadata'].get('to', 'Unknown')}")
        print(f"Relevance: {1-result['distance']:.2%}")
        
        # Extract key content
        doc_lower = result['doc'].lower()
        
        # Look for specific evidence
        if any(term in doc_lower for term in ['expire', 'expiry', 'extension', 'extend', 'validity']):
            print("*** MORTGAGE EXPIRY/EXTENSION EVIDENCE ***")
            
        if any(term in doc_lower for term in ['second', 'reappl', 'again', 'another', 'new application']):
            print("*** POSSIBLE SECOND APPLICATION EVIDENCE ***")
            
        if any(term in doc_lower for term in ['fee', 'cost', '£', 'charge', 'payment']):
            print("*** FINANCIAL IMPACT EVIDENCE ***")
            
        # Show relevant excerpts
        keywords = ['mortgage', 'expire', 'extend', 'application', 'broker', 'fee', 'deadline', 'pressure']
        for keyword in keywords:
            if keyword in doc_lower:
                start = max(0, doc_lower.find(keyword) - 150)
                end = min(len(result['doc']), doc_lower.find(keyword) + 150)
                excerpt = result['doc'][start:end].strip()
                if excerpt:
                    print(f"\nContext for '{keyword}': ...{excerpt}...")
                    break
        
        # Store findings
        findings['mortgage_extension_evidence'].append({
            'date': result['date'],
            'subject': result['subject'],
            'from': result['metadata'].get('from', ''),
            'relevance': 1-result['distance'],
            'preview': result['doc'][:500]
        })
    
    # Save findings
    with open('mortgage_extension_findings.json', 'w') as f:
        json.dump(findings, f, indent=2)
    
    print(f"\n\nFindings saved to mortgage_extension_findings.json")
    
    # Also search for specific dates and mortgage timeline
    print("\n\n=== SEARCHING FOR MORTGAGE TIMELINE ===")
    
    timeline_queries = [
        "mortgage offer June 2023",
        "mortgage offer July 2023", 
        "mortgage offer August 2023",
        "mortgage offer September 2023",
        "mortgage offer October 2023",
        "mortgage offer November 2023",
        "mortgage offer December 2023",
        "mortgage application 2023",
        "mortgage approval 2023",
        "mortgage 3 month validity",
        "mortgage 6 month validity"
    ]
    
    for query in timeline_queries:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=["metadatas", "documents"]
        )
        
        if results['ids'][0]:
            print(f"\n{query}:")
            for metadata, doc in zip(results['metadatas'][0], results['documents'][0]):
                date = metadata.get('date', 'Unknown')
                subject = metadata.get('subject', 'No subject')
                if '2023' in date:
                    print(f"  - {date}: {subject}")

if __name__ == "__main__":
    search_mortgage_extensions()