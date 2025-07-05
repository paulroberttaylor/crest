#!/usr/bin/env python3
"""
Search for completion delay evidence without strict date filtering
"""

import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime

class CompletionEvidenceSearcher:
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
    
    def search_key_phrases(self):
        """Search for specific key phrases related to completion delays."""
        
        # Key phrases to search for
        searches = [
            {
                'query': 'I do not believe we will be ready to complete on 31st October',
                'description': 'October 24 Critical Email'
            },
            {
                'query': 'Trinity Rose survey access property appointment',
                'description': 'Trinity Rose Access Issues'
            },
            {
                'query': 'redemption statement waiting delay Crest',
                'description': 'Redemption Statement Delays'
            },
            {
                'query': 'consent proposed works outstanding',
                'description': 'Consent for Works Issues'
            },
            {
                'query': 'updated contract amendments full replies enquiries',
                'description': 'Contract Documentation Issues'
            },
            {
                'query': 'URGENT 10 Colt View December exchange',
                'description': 'December Urgent Exchanges'
            },
            {
                'query': 'Hannah Rafferty October November December 2023',
                'description': 'Hannah Rafferty Timeline'
            },
            {
                'query': 'Natalie Haigh Plot 34 completion delay',
                'description': 'Natalie Haigh Communications'
            }
        ]
        
        all_results = []
        
        for search in searches:
            print(f"\n{'='*80}")
            print(f"SEARCHING FOR: {search['description']}")
            print(f"Query: {search['query']}")
            print('='*80)
            
            results = self.collection.query(
                query_texts=[search['query']],
                n_results=10
            )
            
            if results['ids'][0]:
                for i, (doc_id, metadata, document, distance) in enumerate(zip(
                    results['ids'][0], 
                    results['metadatas'][0], 
                    results['documents'][0],
                    results['distances'][0]
                )):
                    score = 1 - distance
                    if score > 0.3:  # Relevance threshold
                        date = metadata.get('date', 'No date')
                        subject = metadata.get('subject', 'No subject')
                        from_addr = metadata.get('from', 'Unknown')
                        to_addr = metadata.get('to', 'Unknown')
                        
                        print(f"\n{i+1}. Score: {score:.2f}")
                        print(f"   Date: {date}")
                        print(f"   From: {from_addr}")
                        print(f"   To: {to_addr}")
                        print(f"   Subject: {subject}")
                        
                        # Extract key quotes
                        lines = document.split('\n')
                        print("   Key content:")
                        content_found = False
                        
                        for line in lines:
                            line_strip = line.strip()
                            line_lower = line_strip.lower()
                            
                            # Look for specific evidence
                            if any(phrase in line_lower for phrase in [
                                'i do not believe we will be ready',
                                'trinity rose',
                                'redemption statement',
                                'consent for proposed works',
                                'updated contract',
                                'full replies',
                                'urgent',
                                'cannot complete',
                                'delay',
                                'waiting for',
                                'outstanding'
                            ]):
                                if len(line_strip) > 20:
                                    print(f"   - \"{line_strip[:150]}...\"")
                                    content_found = True
                        
                        if not content_found:
                            # Show first meaningful line
                            for line in lines[5:]:
                                if len(line.strip()) > 50:
                                    print(f"   - \"{line.strip()[:150]}...\"")
                                    break
            else:
                print("   No relevant results found.")
        
        # Now do a specific October 2023 search
        print(f"\n{'='*80}")
        print("SPECIFIC OCTOBER 2023 COMPLETION SEARCH")
        print('='*80)
        
        october_results = self.collection.query(
            query_texts=["October 2023 completion Plot 34 Colt View ready exchange"],
            n_results=50
        )
        
        october_emails = []
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            october_results['ids'][0], 
            october_results['metadatas'][0], 
            october_results['documents'][0],
            october_results['distances'][0]
        )):
            date = metadata.get('date', '')
            if '2023-10' in date:
                october_emails.append({
                    'date': date,
                    'subject': metadata.get('subject', ''),
                    'from': metadata.get('from', ''),
                    'document': document,
                    'score': 1 - distance
                })
        
        # Sort by date
        october_emails.sort(key=lambda x: x['date'])
        
        print(f"\nFound {len(october_emails)} October 2023 emails about completion")
        for email in october_emails:
            if email['score'] > 0.4:
                print(f"\n{email['date'][:10]}: {email['subject']}")
                print(f"From: {email['from']}")
                
                # Look for key content
                doc_lower = email['document'].lower()
                if 'ready' in doc_lower or 'complete' in doc_lower or 'exchange' in doc_lower:
                    lines = email['document'].split('\n')
                    for line in lines:
                        if any(term in line.lower() for term in ['ready', 'complete', 'exchange', 'october 31']):
                            print(f"  \"{line.strip()[:120]}...\"")
                            break

def main():
    searcher = CompletionEvidenceSearcher()
    searcher.search_key_phrases()

if __name__ == "__main__":
    main()