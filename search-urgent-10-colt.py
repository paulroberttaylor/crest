#!/usr/bin/env python3
"""
Search for the URGENT: 10 Colt View email thread
"""

import chromadb
from chromadb.utils import embedding_functions
from collections import defaultdict

class UrgentThreadSearcher:
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
    
    def search_urgent_thread(self):
        """Search for URGENT: 10 Colt View emails."""
        
        print("SEARCHING FOR 'URGENT: 10 COLT VIEW' THREAD")
        print("=" * 80)
        
        # Search for the urgent thread
        results = self.collection.query(
            query_texts=["URGENT 10 Colt View December 2023"],
            n_results=100
        )
        
        urgent_emails = []
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            subject = metadata.get('subject', '')
            if 'urgent' in subject.lower() and ('10 colt' in subject.lower() or 'colt view' in subject.lower()):
                urgent_emails.append({
                    'date': metadata.get('date', ''),
                    'from': metadata.get('from', ''),
                    'to': metadata.get('to', ''),
                    'subject': subject,
                    'document': document,
                    'score': 1 - distance
                })
        
        # Sort by date
        urgent_emails.sort(key=lambda x: x['date'])
        
        print(f"\nFound {len(urgent_emails)} URGENT: 10 Colt View emails\n")
        
        # Analyze sender patterns
        from_paul = 0
        from_crest = 0
        from_solicitor = 0
        
        for email in urgent_emails:
            from_addr = email['from'].lower()
            if 'paulroberttaylor' in from_addr:
                from_paul += 1
            elif 'crestnicholson.com' in from_addr:
                from_crest += 1
            elif 'bramsdonandchilds.com' in from_addr:
                from_solicitor += 1
        
        print(f"Email breakdown:")
        print(f"- From Paul: {from_paul}")
        print(f"- From Crest: {from_crest}")
        print(f"- From Solicitor: {from_solicitor}")
        
        print("\n\nDETAILED TIMELINE:")
        print("-" * 80)
        
        # Group by date
        by_date = defaultdict(list)
        for email in urgent_emails:
            date_key = email['date'][:10] if email['date'] else 'Unknown'
            by_date[date_key].append(email)
        
        for date in sorted(by_date.keys()):
            if '2023' in date:  # Focus on 2023
                emails = by_date[date]
                print(f"\n{date} ({len(emails)} emails):")
                
                for email in emails:
                    time = email['date'][11:16] if len(email['date']) > 16 else ''
                    from_name = email['from'].split('<')[0].strip()
                    to_name = email['to'].split('<')[0].strip()
                    
                    print(f"  {time} - {from_name} → {to_name}")
                    print(f"         Subject: {email['subject']}")
                    
                    # Extract key content
                    doc_lower = email['document'].lower()
                    if any(term in doc_lower for term in ['waiting', 'delay', 'outstanding', 'urgent', 'chasing']):
                        lines = email['document'].split('\n')
                        for line in lines[4:]:  # Skip headers
                            line_lower = line.lower()
                            if any(term in line_lower for term in ['waiting', 'delay', 'outstanding', 'urgent', 'still']):
                                if len(line.strip()) > 30:
                                    print(f"         \"{line.strip()[:100]}...\"")
                                    break
        
        # Look for specific completion obstacles
        print("\n\nCOMPLETION OBSTACLES MENTIONED:")
        print("-" * 80)
        
        obstacles = defaultdict(int)
        
        for email in urgent_emails:
            doc_lower = email['document'].lower()
            
            if 'redemption statement' in doc_lower:
                obstacles['Redemption Statement'] += 1
            if 'consent' in doc_lower and 'works' in doc_lower:
                obstacles['Consent for Works'] += 1
            if 'contract' in doc_lower and ('updated' in doc_lower or 'amendment' in doc_lower):
                obstacles['Contract Updates'] += 1
            if 'documentation' in doc_lower and 'outstanding' in doc_lower:
                obstacles['Outstanding Documentation'] += 1
            if 'fence' in doc_lower:
                obstacles['Fence Issue'] += 1
        
        for obstacle, count in sorted(obstacles.items(), key=lambda x: x[1], reverse=True):
            print(f"- {obstacle}: mentioned in {count} emails")
        
        # Extract Hannah Rafferty's October 24 quote if present
        print("\n\nKEY QUOTES:")
        print("-" * 80)
        
        for email in urgent_emails:
            if 'hannah rafferty' in email['from'].lower():
                doc_lower = email['document'].lower()
                if 'i do not believe we will be ready' in doc_lower:
                    print(f"\n{email['date'][:16]} - Hannah Rafferty:")
                    lines = email['document'].split('\n')
                    for line in lines:
                        if 'i do not believe we will be ready' in line.lower():
                            print(f"  \"{line.strip()}\"")

def main():
    searcher = UrgentThreadSearcher()
    searcher.search_urgent_thread()

if __name__ == "__main__":
    main()