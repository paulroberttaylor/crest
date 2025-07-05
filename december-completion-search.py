#!/usr/bin/env python3
"""
Search for emails from December 15-18, 2023 around completion day
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json

# Need to activate the virtual environment first
activate_this = os.path.join(os.path.dirname(__file__), 'email_indexer_env/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

import chromadb
from chromadb.utils import embedding_functions

def search_december_completion():
    """Search for completion day emails."""
    
    client = chromadb.PersistentClient(path="./chromadb_emails_quick")
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_collection(
        name="emails_quick",
        embedding_function=embedding_function
    )
    
    # Multiple searches to catch everything
    searches = [
        "December 18 2023 completion exchange contract",
        "December 15 16 17 2023 contract",
        "Hannah Rafferty December 2023",
        "Natalie Haigh December 2023", 
        "Maja Janusz December 2023",
        "urgent completion december",
        "exchange contracts final",
        "completion today urgent",
        "contract issues december"
    ]
    
    all_emails = {}
    
    for search in searches:
        print(f"Searching: {search}")
        results = collection.query(
            query_texts=[search],
            n_results=50
        )
        
        for i, (doc_id, meta, doc, dist) in enumerate(zip(
            results['ids'][0],
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            date_str = meta.get('date', '')
            if date_str and '2023-12' in date_str:
                # Parse date
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if dt.day >= 15 and dt.day <= 18:
                        key = f"{date_str}_{meta.get('from', '')}"
                        if key not in all_emails:
                            all_emails[key] = {
                                'date': date_str,
                                'datetime': dt,
                                'from': meta.get('from', ''),
                                'to': meta.get('to', ''),
                                'subject': meta.get('subject', ''),
                                'content': doc,
                                'distance': dist
                            }
                except:
                    pass
    
    # Sort by datetime
    sorted_emails = sorted(all_emails.values(), key=lambda x: x['datetime'])
    
    print(f"\nFound {len(sorted_emails)} emails from December 15-18, 2023")
    print("="*80)
    
    # Output results
    with open('december_completion_emails.txt', 'w') as f:
        f.write("DECEMBER 15-18, 2023 COMPLETION EMAILS\n")
        f.write("="*80 + "\n\n")
        
        for email in sorted_emails:
            dt = email['datetime']
            
            output = f"""
Date: {dt.strftime('%Y-%m-%d %H:%M:%S')} ({dt.strftime('%A')})
From: {email['from']}
To: {email['to']}
Subject: {email['subject']}

Full Content:
{email['content']}

{'='*80}
"""
            print(output)
            f.write(output)
    
    print(f"\nResults saved to: december_completion_emails.txt")
    
    # Also create a focused timeline
    print("\n\nKEY TIMELINE POINTS:")
    print("="*50)
    
    for email in sorted_emails:
        dt = email['datetime']
        from_addr = email['from']
        subject = email['subject']
        
        # Identify sender
        sender = "Unknown"
        if 'hannah' in from_addr.lower():
            sender = "Hannah Rafferty (Solicitor)"
        elif 'natalie' in from_addr.lower():
            sender = "Natalie Haigh (Crest)"
        elif 'maja' in from_addr.lower():
            sender = "Maja Janusz (Crest Solicitor)"
        elif 'paul' in from_addr.lower():
            sender = "Paul Taylor"
        elif 'jade' in from_addr.lower():
            sender = "Jade"
        
        print(f"\n{dt.strftime('%b %d %H:%M')} - {sender}")
        print(f"Subject: {subject}")
        
        # Extract key content
        content_lower = email['content'].lower()
        lines = email['content'].split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(term in line_lower for term in [
                'exchange', 'complet', 'contract', 'today', 'urgent', 
                'final', 'issue', 'problem', 'delay', 'confirm', 
                'not ready', 'ready', 'agreed', 'signed'
            ]):
                if line.strip() and len(line.strip()) > 10:
                    print(f"  → {line.strip()[:200]}")

if __name__ == "__main__":
    search_december_completion()