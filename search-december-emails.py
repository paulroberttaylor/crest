#!/usr/bin/env python3
"""
Search for all December 2023 emails to find completion details
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

def search_all_december():
    """Search for all December 2023 emails."""
    
    client = chromadb.PersistentClient(path="./chromadb_emails_quick")
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_collection(
        name="emails_quick",
        embedding_function=embedding_function
    )
    
    # Get ALL documents and filter by date
    print("Getting all emails from database...")
    all_results = collection.get()
    
    december_emails = []
    
    for i, (doc_id, meta, doc) in enumerate(zip(
        all_results['ids'],
        all_results['metadatas'], 
        all_results['documents']
    )):
        date_str = meta.get('date', '')
        if date_str and '2023-12' in date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                december_emails.append({
                    'date': date_str,
                    'datetime': dt,
                    'from': meta.get('from', ''),
                    'to': meta.get('to', ''),
                    'subject': meta.get('subject', ''),
                    'content': doc
                })
            except:
                pass
    
    # Sort by datetime
    december_emails.sort(key=lambda x: x['datetime'])
    
    print(f"\nFound {len(december_emails)} emails from December 2023")
    
    # Filter for completion-related
    completion_emails = []
    for email in december_emails:
        content_lower = email['content'].lower()
        subject_lower = email['subject'].lower()
        
        # Check if related to completion/contract
        if any(term in content_lower or term in subject_lower for term in [
            'complet', 'exchange', 'contract', 'colt view', 'plot 34',
            'hannah rafferty', 'natalie haigh', 'maja janusz'
        ]):
            completion_emails.append(email)
    
    print(f"Found {len(completion_emails)} completion-related emails")
    
    # Focus on Dec 15-18
    key_dates = []
    for email in completion_emails:
        if 15 <= email['datetime'].day <= 18:
            key_dates.append(email)
    
    print(f"Found {len(key_dates)} emails from Dec 15-18")
    
    # Output all December completion emails
    with open('december_all_completion_emails.txt', 'w') as f:
        f.write("ALL DECEMBER 2023 COMPLETION-RELATED EMAILS\n")
        f.write("="*80 + "\n\n")
        
        current_day = None
        
        for email in completion_emails:
            dt = email['datetime']
            day = dt.strftime('%Y-%m-%d')
            
            if day != current_day:
                current_day = day
                f.write(f"\n\n{'='*30} {dt.strftime('%A, %B %d, %Y')} {'='*30}\n\n")
            
            output = f"""
Time: {dt.strftime('%H:%M:%S')}
From: {email['from']}
To: {email['to']}
Subject: {email['subject']}

{email['content']}

{'-'*80}
"""
            f.write(output)
            
            # Print key emails
            if 15 <= dt.day <= 18:
                print(f"\n{dt.strftime('%b %d %H:%M')} - {email['from']}")
                print(f"Subject: {email['subject']}")
                
                # Show key lines
                lines = email['content'].split('\n')
                for line in lines[:10]:  # First 10 lines
                    if line.strip():
                        print(f"  {line.strip()[:100]}")
    
    print(f"\nAll emails saved to: december_all_completion_emails.txt")

if __name__ == "__main__":
    search_all_december()