#!/usr/bin/env python3
"""
Search for Natalie Haigh's specific statements about gutters
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
    
    # Search for Natalie Haigh emails about gutters
    results = collection.query(
        query_texts=["Natalie Haigh gutters checked cleared no debris"],
        n_results=50,
        include=['documents', 'metadatas', 'distances']
    )
    
    print("Searching for Natalie Haigh's statements about gutters...")
    print("="*80)
    
    findings = []
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        # Check if email is from or to Natalie Haigh
        from_email = metadata.get('from', '').lower()
        to_email = metadata.get('to', '').lower()
        
        if 'natalie.haigh' in from_email or 'natalie.haigh' in to_email:
            # Check if content mentions gutters
            content_lower = doc.lower()
            if 'gutter' in content_lower:
                # Extract relevant sentences
                lines = doc.split('\n')
                relevant_lines = []
                for line in lines:
                    if 'gutter' in line.lower():
                        relevant_lines.append(line)
                
                if relevant_lines:
                    print(f"\n--- Email {i+1} ---")
                    print(f"Date: {metadata.get('date', 'Unknown')}")
                    print(f"From: {metadata.get('from', 'Unknown')}")
                    print(f"To: {metadata.get('to', 'Unknown')}")
                    print(f"Subject: {metadata.get('subject', 'No subject')}")
                    print(f"\nRelevant content:")
                    for line in relevant_lines[:5]:  # Show up to 5 relevant lines
                        print(f"  > {line.strip()}")
                    
                    findings.append({
                        'date': metadata.get('date', 'Unknown'),
                        'from': metadata.get('from', 'Unknown'),
                        'to': metadata.get('to', 'Unknown'),
                        'subject': metadata.get('subject', 'No subject'),
                        'relevant_lines': relevant_lines
                    })
    
    print(f"\n\nFound {len(findings)} emails involving Natalie Haigh and gutters")
    
    # Save findings
    with open('natalie_haigh_gutters.json', 'w') as f:
        json.dump(findings, f, indent=2)

if __name__ == "__main__":
    main()