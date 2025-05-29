#!/usr/bin/env python3
"""
Search and summarize emails from specific senders using ChromaDB
"""

import chromadb
from chromadb.utils import embedding_functions
import sys
from collections import defaultdict
from datetime import datetime

class EmailAnalyzer:
    def __init__(self):
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails_quick")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_collection(
            name="emails_quick",
            embedding_function=self.embedding_function
        )
        print(f"Connected to {self.collection.count()} indexed emails\n")
    
    def search_from_person_about_topic(self, person_name: str, topic: str, n_results: int = 100):
        """Use ChromaDB's semantic search to find emails from a person about a topic."""
        
        # First, do a semantic search for the topic
        print(f"Searching for emails about '{topic}'...")
        results = self.collection.query(
            query_texts=[topic],
            n_results=n_results
        )
        
        # Filter by sender
        filtered_emails = []
        person_lower = person_name.lower()
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            from_addr = metadata.get('from', '').lower()
            if person_lower in from_addr:
                filtered_emails.append({
                    'date': metadata.get('date', ''),
                    'subject': metadata.get('subject', ''),
                    'document': document,
                    'score': 1 - distance,
                    'metadata': metadata
                })
        
        # Sort by date
        filtered_emails.sort(key=lambda x: x['date'])
        
        return filtered_emails
    
    def summarize_contract_emails(self, person_name: str):
        """Summarize all contract-related emails from a person."""
        
        # Search for multiple contract-related terms
        all_emails = []
        topics = [
            "contract exchange completion",
            "urgent delay waiting",
            "plot 34 purchase",
            "10 colt view",
            "ready to complete",
            "completion date"
        ]
        
        seen_ids = set()
        
        for topic in topics:
            emails = self.search_from_person_about_topic(person_name, topic, n_results=30)
            for email in emails:
                # Avoid duplicates
                email_key = f"{email['date']}_{email['subject']}"
                if email_key not in seen_ids:
                    seen_ids.add(email_key)
                    all_emails.append(email)
        
        # Sort by date
        all_emails.sort(key=lambda x: x['date'])
        
        print(f"\nFound {len(all_emails)} contract-related emails from {person_name}\n")
        print("=" * 80)
        
        # Group by month for summary
        by_month = defaultdict(list)
        for email in all_emails:
            if email['date']:
                month_key = email['date'][:7]  # YYYY-MM
                by_month[month_key].append(email)
        
        # Summarize by month
        for month in sorted(by_month.keys()):
            emails = by_month[month]
            print(f"\n{month} ({len(emails)} emails):")
            print("-" * 40)
            
            for email in emails:
                date = email['date'][:10] if email['date'] else 'Unknown'
                subject = email['subject'][:60] + '...' if len(email['subject']) > 60 else email['subject']
                
                # Extract key content
                doc = email['document'].lower()
                key_phrases = []
                
                if 'not ready' in doc or 'cannot complete' in doc:
                    key_phrases.append("❌ Not ready/Cannot complete")
                if 'urgent' in doc:
                    key_phrases.append("🚨 Urgent")
                if 'exchange' in doc and ('today' in doc or 'tomorrow' in doc):
                    key_phrases.append("📝 Exchange imminent")
                if 'completion' in doc and any(month in doc for month in ['october', 'november', 'december']):
                    key_phrases.append("📅 Completion date discussed")
                if 'delay' in doc or 'late' in doc:
                    key_phrases.append("⏰ Delay mentioned")
                if 'contract' in doc and ('send' in doc or 'sent' in doc or 'receive' in doc):
                    key_phrases.append("📄 Contract transfer")
                
                print(f"{date}: {subject}")
                if key_phrases:
                    print(f"   Key points: {', '.join(key_phrases)}")
                
                # Show relevant excerpt
                lines = email['document'].split('\n')
                for line in lines[4:]:  # Skip headers
                    line_lower = line.lower()
                    if any(term in line_lower for term in ['ready', 'complete', 'exchange', 'delay', 'contract', 'urgent']):
                        excerpt = line.strip()[:150]
                        if excerpt:
                            print(f"   \"{excerpt}...\"")
                            break
        
        print("\n" + "=" * 80)
        print("\nSUMMARY OF KEY EVENTS:")
        print("-" * 40)
        
        # Extract key timeline events
        key_events = []
        
        for email in all_emails:
            doc = email['document']
            date = email['date'][:10] if email['date'] else 'Unknown'
            
            if 'i do not believe we will be ready' in doc.lower():
                key_events.append(f"{date}: Solicitor states not ready to complete")
            elif 'exchange today' in doc.lower() or 'exchanging today' in doc.lower():
                key_events.append(f"{date}: Attempting to exchange")
            elif 'completion' in doc.lower() and 'december' in doc.lower():
                key_events.append(f"{date}: December completion discussed")
            elif 'still waiting' in doc.lower() or 'chasing' in doc.lower():
                key_events.append(f"{date}: Still waiting/chasing")
        
        for event in key_events[:10]:  # Show first 10 key events
            print(f"• {event}")

def main():
    if len(sys.argv) > 1:
        person = ' '.join(sys.argv[1:])
    else:
        person = "Hannah Rafferty"
    
    analyzer = EmailAnalyzer()
    analyzer.summarize_contract_emails(person)

if __name__ == "__main__":
    main()