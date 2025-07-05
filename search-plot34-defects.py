#!/usr/bin/env python3
"""
Search for Plot 34 defects list and completion issues
"""

import chromadb
from chromadb.config import Settings
import json
from datetime import datetime

def main():
    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path="chromadb_emails_quick",
        settings=Settings(anonymized_telemetry=False)
    )
    
    collection = client.get_collection("emails_quick")
    
    # Multiple targeted searches
    searches = [
        {
            "query": "Plot 34 Albany Wood defects January 2024",
            "description": "Defects found at completion"
        },
        {
            "query": "45 defects completion day",
            "description": "45 defects on completion"
        },
        {
            "query": "build manager checked 15 times property",
            "description": "Build manager claiming 15 checks"
        },
        {
            "query": "gutters cleaned checked Natalie Haigh",
            "description": "Natalie Haigh statements about gutters"
        }
    ]
    
    all_findings = []
    
    for search in searches:
        print(f"\n{'='*80}")
        print(f"Searching: {search['description']}")
        print(f"Query: {search['query']}")
        print("="*80)
        
        results = collection.query(
            query_texts=[search['query']],
            n_results=20,
            include=['documents', 'metadatas', 'distances']
        )
        
        search_findings = []
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            date_str = metadata.get('date', '')
            
            # Focus on 2023-2024 emails
            if any(year in date_str for year in ['2023', '2024']):
                relevance = 1 - distance
                if relevance > 0.3:  # Only show relevant results
                    print(f"\n--- Email {i+1} ---")
                    print(f"Date: {metadata.get('date', 'Unknown')}")
                    print(f"From: {metadata.get('from', 'Unknown')}")
                    print(f"To: {metadata.get('to', 'Unknown')}")
                    print(f"Subject: {metadata.get('subject', 'No subject')}")
                    print(f"Relevance: {relevance:.2f}")
                    
                    # Show first 300 chars of content
                    print(f"\nContent preview:")
                    content_preview = doc[:300].replace('\n', '\n  ')
                    print(f"  {content_preview}...")
                    
                    # Look for specific keywords
                    content_lower = doc.lower()
                    if any(keyword in content_lower for keyword in ['defect', 'gutter', 'checked', '15', '45', 'natalie']):
                        print("\n  [Contains relevant keywords]")
                    
                    search_findings.append({
                        'date': metadata.get('date', 'Unknown'),
                        'from': metadata.get('from', 'Unknown'),
                        'to': metadata.get('to', 'Unknown'),
                        'subject': metadata.get('subject', 'No subject'),
                        'relevance': relevance,
                        'content_preview': doc[:500]
                    })
        
        all_findings.append({
            'search': search['description'],
            'query': search['query'],
            'findings': search_findings
        })
    
    # Save all findings
    with open('plot34_defects_search.json', 'w') as f:
        json.dump(all_findings, f, indent=2)
    
    print("\n\nResults saved to plot34_defects_search.json")

if __name__ == "__main__":
    main()