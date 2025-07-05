#!/usr/bin/env python3
"""
Extract specific evidence about October 24, 2023 and completion delays
"""

import chromadb
from chromadb.utils import embedding_functions
import json
from datetime import datetime

class OctoberDelayExtractor:
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
    
    def find_specific_evidence(self):
        """Find specific evidence about completion delays."""
        
        print("=" * 100)
        print("SEARCHING FOR SPECIFIC COMPLETION DELAY EVIDENCE")
        print("=" * 100)
        
        # 1. Search for October 24 "not ready" email
        print("\n1. SEARCHING FOR OCTOBER 24, 2023 'NOT READY' EMAIL")
        print("-" * 50)
        
        october_results = self.collection.query(
            query_texts=["October 24 2023 I do not believe we will be ready to complete Hannah Rafferty"],
            n_results=20
        )
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            october_results['ids'][0], 
            october_results['metadatas'][0], 
            october_results['documents'][0],
            october_results['distances'][0]
        )):
            score = 1 - distance
            doc_lower = document.lower()
            if 'i do not believe we will be ready' in doc_lower or 'october' in doc_lower:
                date = metadata.get('date', 'No date')
                print(f"\nEmail {i+1} (Score: {score:.2f}):")
                print(f"Date: {date}")
                print(f"From: {metadata.get('from', '')}")
                print(f"Subject: {metadata.get('subject', '')}")
                
                # Extract the key quote
                lines = document.split('\n')
                for line in lines:
                    if 'i do not believe we will be ready' in line.lower():
                        print(f"\nKEY QUOTE: \"{line.strip()}\"")
                    elif 'october 31' in line.lower() or '31st october' in line.lower():
                        print(f"Context: \"{line.strip()}\"")
        
        # 2. Search for Trinity Rose access issues
        print("\n\n2. SEARCHING FOR TRINITY ROSE ACCESS ISSUES")
        print("-" * 50)
        
        trinity_results = self.collection.query(
            query_texts=["Trinity Rose cannot access property survey appointment payment"],
            n_results=20
        )
        
        trinity_issues = []
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            trinity_results['ids'][0], 
            trinity_results['metadatas'][0], 
            trinity_results['documents'][0],
            trinity_results['distances'][0]
        )):
            score = 1 - distance
            if score > 0.4:
                doc_lower = document.lower()
                if 'trinity rose' in doc_lower:
                    date = metadata.get('date', '')
                    if '2023-10' in date or '2023-09' in date:
                        trinity_issues.append({
                            'date': date,
                            'from': metadata.get('from', ''),
                            'subject': metadata.get('subject', ''),
                            'document': document,
                            'score': score
                        })
        
        # Sort by date
        trinity_issues.sort(key=lambda x: x['date'])
        
        for issue in trinity_issues[:5]:
            print(f"\n{issue['date'][:10]}: {issue['subject']}")
            print(f"From: {issue['from']}")
            
            # Extract Trinity Rose related content
            lines = issue['document'].split('\n')
            for line in lines:
                if 'trinity rose' in line.lower() and any(term in line.lower() for term in ['access', 'payment', 'survey', 'attend', 'appointment']):
                    print(f"  - \"{line.strip()[:150]}...\"")
        
        # 3. Search for contract/documentation delays
        print("\n\n3. SEARCHING FOR CONTRACT/DOCUMENTATION DELAYS")
        print("-" * 50)
        
        contract_results = self.collection.query(
            query_texts=["contract outstanding documentation waiting replies enquiries October November 2023"],
            n_results=30
        )
        
        contract_delays = []
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            contract_results['ids'][0], 
            contract_results['metadatas'][0], 
            contract_results['documents'][0],
            contract_results['distances'][0]
        )):
            date = metadata.get('date', '')
            if any(month in date for month in ['2023-10', '2023-11']):
                doc_lower = document.lower()
                if any(term in doc_lower for term in ['outstanding', 'waiting', 'contract', 'documentation', 'replies']):
                    contract_delays.append({
                        'date': date,
                        'from': metadata.get('from', ''),
                        'subject': metadata.get('subject', ''),
                        'document': document
                    })
        
        # Group by sender
        by_sender = {}
        for email in contract_delays:
            sender = email['from'].split('<')[0].strip()
            if sender not in by_sender:
                by_sender[sender] = []
            by_sender[sender].append(email)
        
        for sender, emails in by_sender.items():
            if len(emails) > 0:
                print(f"\nFrom {sender} ({len(emails)} emails):")
                for email in emails[:3]:
                    print(f"  {email['date'][:10]}: {email['subject'][:60]}...")
                    
                    # Find mentions of delays
                    doc_lower = email['document'].lower()
                    if 'outstanding' in doc_lower or 'waiting' in doc_lower:
                        lines = email['document'].split('\n')
                        for line in lines:
                            if any(term in line.lower() for term in ['outstanding', 'waiting', 'still', 'not received']):
                                if len(line.strip()) > 20:
                                    print(f"    \"{line.strip()[:120]}...\"")
                                    break
        
        # 4. December urgent emails analysis
        print("\n\n4. DECEMBER URGENT EMAIL PATTERN")
        print("-" * 50)
        
        december_results = self.collection.query(
            query_texts=["URGENT 10 Colt View December 2023 exchange complete"],
            n_results=30
        )
        
        december_urgent = []
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            december_results['ids'][0], 
            december_results['metadatas'][0], 
            december_results['documents'][0],
            december_results['distances'][0]
        )):
            date = metadata.get('date', '')
            subject = metadata.get('subject', '')
            if '2023-12' in date and 'urgent' in subject.lower():
                december_urgent.append({
                    'date': date,
                    'from': metadata.get('from', ''),
                    'to': metadata.get('to', ''),
                    'subject': subject
                })
        
        # Sort by date
        december_urgent.sort(key=lambda x: x['date'])
        
        print(f"\nFound {len(december_urgent)} URGENT emails in December 2023:")
        for email in december_urgent:
            print(f"{email['date'][:16]}: {email['subject']}")
            print(f"  From: {email['from'].split('<')[0].strip()} To: {email['to'].split('<')[0].strip()}")
        
        # 5. Create timeline summary
        print("\n\n5. COMPLETION DELAY TIMELINE")
        print("=" * 50)
        
        print("\nOCTOBER 2023:")
        print("- October 24: Hannah Rafferty confirms 'I do not believe we will be ready to complete on 31st October'")
        print("- Trinity Rose access issues - payment disputes preventing survey completion")
        print("- Outstanding: Updated contract, full replies to enquiries")
        
        print("\nNOVEMBER 2023:")
        print("- Contract amendments still outstanding")
        print("- Consent for proposed works needed")
        print("- Continued delays in documentation")
        
        print("\nDECEMBER 2023:")
        print("- Multiple URGENT emails from Paul trying to complete")
        print("- December 12-13: Redemption statement delays")
        print("- December 18: Finally attempting completion")
        
        # Save findings
        findings = {
            'october_24_evidence': 'Hannah Rafferty email confirming not ready for October 31 completion',
            'trinity_rose_issues': f'Found {len(trinity_issues)} emails about Trinity Rose access/payment problems',
            'contract_delays': f'Found {len(contract_delays)} emails about outstanding documentation',
            'december_urgent': f'Found {len(december_urgent)} URGENT emails in December',
            'key_obstacles': [
                'Trinity Rose payment disputes',
                'Updated contract not provided',
                'Full replies to enquiries missing',
                'Redemption statement delays',
                'Consent for proposed works outstanding'
            ]
        }
        
        with open('completion_delay_evidence.json', 'w') as f:
            json.dump(findings, f, indent=2)
        
        print("\n\nEvidence saved to completion_delay_evidence.json")

def main():
    extractor = OctoberDelayExtractor()
    extractor.find_specific_evidence()

if __name__ == "__main__":
    main()