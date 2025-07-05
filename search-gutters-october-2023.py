#!/usr/bin/env python3
"""
Search for emails about gutters in October 2023, specifically looking for Natalie Haigh's responses
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
    
    # Search for emails about gutters in the October 2023 timeframe
    results = collection.query(
        query_texts=["gutters cleaned cleared checked October 2023"],
        n_results=100,
        include=['documents', 'metadatas', 'distances']
    )
    
    print("Searching for gutter-related emails in October 2023...")
    print("="*80)
    
    findings = []
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        date_str = metadata.get('date', '')
        if '2023-10' in date_str or '2023-09' in date_str or '2023-11' in date_str:
            # Check if content mentions gutters
            content_lower = doc.lower()
            if 'gutter' in content_lower:
                print(f"\n--- Email {i+1} ---")
                print(f"Date: {metadata.get('date', 'Unknown')}")
                print(f"From: {metadata.get('from', 'Unknown')}")
                print(f"To: {metadata.get('to', 'Unknown')}")
                print(f"Subject: {metadata.get('subject', 'No subject')}")
                print(f"Relevance: {1 - distance:.2f}")
                
                # Extract relevant content around "gutter"
                lines = doc.split('\n')
                for j, line in enumerate(lines):
                    if 'gutter' in line.lower():
                        # Show context (2 lines before and after)
                        start = max(0, j-2)
                        end = min(len(lines), j+3)
                        print(f"\nContext:")
                        for k in range(start, end):
                            if k == j:
                                print(f">>> {lines[k]}")
                            else:
                                print(f"    {lines[k]}")
                
                findings.append({
                    'date': metadata.get('date', 'Unknown'),
                    'from': metadata.get('from', 'Unknown'),
                    'to': metadata.get('to', 'Unknown'),
                    'subject': metadata.get('subject', 'No subject'),
                    'content_snippet': doc[:500]
                })
    
    print(f"\n\nFound {len(findings)} emails about gutters in Sept-Nov 2023")
    
    # Save findings
    with open('gutters_october_2023.json', 'w') as f:
        json.dump(findings, f, indent=2)

if __name__ == "__main__":
    main()