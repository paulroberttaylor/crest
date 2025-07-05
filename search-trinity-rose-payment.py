#!/usr/bin/env python3
"""
Search for Trinity Rose payment and access issues
"""

import chromadb
from chromadb.utils import embedding_functions

class TrinityRoseSearcher:
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
    
    def search_trinity_rose_issues(self):
        """Search for Trinity Rose payment and access issues."""
        
        print("TRINITY ROSE PAYMENT AND ACCESS ISSUES")
        print("=" * 80)
        
        # Key Trinity Rose searches
        searches = [
            "Trinity Rose will not attend unless they are compensated",
            "Trinity Rose payment £1300 invoice costs",
            "Richard Kirby Trinity Rose payment confirmation",
            "Trinity Rose has not been instructed by Crest",
            "Trinity Rose October 11 appointment survey",
            "Crest reneged on agreeing to pay Trinity Rose fees"
        ]
        
        all_trinity_emails = []
        seen = set()
        
        for query in searches:
            print(f"\nSearching: {query}")
            results = self.collection.query(
                query_texts=[query],
                n_results=10
            )
            
            for i, (doc_id, metadata, document, distance) in enumerate(zip(
                results['ids'][0], 
                results['metadatas'][0], 
                results['documents'][0],
                results['distances'][0]
            )):
                score = 1 - distance
                if score > 0.35:  # Relevance threshold
                    email_key = f"{metadata.get('date', '')}-{metadata.get('subject', '')}"
                    if email_key not in seen:
                        seen.add(email_key)
                        all_trinity_emails.append({
                            'date': metadata.get('date', ''),
                            'from': metadata.get('from', ''),
                            'to': metadata.get('to', ''),
                            'subject': metadata.get('subject', ''),
                            'document': document,
                            'score': score
                        })
        
        # Sort by date
        all_trinity_emails.sort(key=lambda x: x['date'])
        
        print(f"\n\nFOUND {len(all_trinity_emails)} UNIQUE TRINITY ROSE EMAILS")
        print("=" * 80)
        
        # Extract key evidence
        evidence = {
            'payment_disputes': [],
            'access_issues': [],
            'key_quotes': []
        }
        
        for email in all_trinity_emails:
            if '2023-10' in email['date'] or '2023-09' in email['date']:
                print(f"\n{email['date'][:16]}")
                print(f"From: {email['from'].split('<')[0].strip()}")
                print(f"To: {email['to'].split('<')[0].strip()}")
                print(f"Subject: {email['subject']}")
                
                doc_lower = email['document'].lower()
                lines = email['document'].split('\n')
                
                # Look for key evidence
                for line in lines:
                    line_lower = line.lower()
                    line_strip = line.strip()
                    
                    # Payment issues
                    if 'trinity rose' in line_lower and any(term in line_lower for term in ['payment', 'pay', 'cost', '£1300', 'compensated', 'invoice']):
                        if len(line_strip) > 20:
                            print(f"  💰 PAYMENT: \"{line_strip[:150]}...\"")
                            evidence['payment_disputes'].append({
                                'date': email['date'][:10],
                                'quote': line_strip
                            })
                    
                    # Access issues
                    elif 'trinity rose' in line_lower and any(term in line_lower for term in ['will not attend', 'not instructed', 'access', 'appointment']):
                        if len(line_strip) > 20:
                            print(f"  🚫 ACCESS: \"{line_strip[:150]}...\"")
                            evidence['access_issues'].append({
                                'date': email['date'][:10],
                                'quote': line_strip
                            })
                    
                    # Crest failures
                    elif any(term in line_lower for term in ['reneged', 'failed to honour', 'not appreciating', 'responsibility']):
                        if 'trinity' in line_lower or 'crest' in line_lower:
                            print(f"  ❌ FAILURE: \"{line_strip[:150]}...\"")
                            evidence['key_quotes'].append({
                                'date': email['date'][:10],
                                'quote': line_strip
                            })
        
        # Summary
        print("\n\nSUMMARY OF TRINITY ROSE ISSUES:")
        print("=" * 80)
        
        print("\n1. PAYMENT DISPUTES:")
        for item in evidence['payment_disputes'][:5]:
            print(f"   {item['date']}: \"{item['quote'][:100]}...\"")
        
        print("\n2. ACCESS PROBLEMS:")
        for item in evidence['access_issues'][:5]:
            print(f"   {item['date']}: \"{item['quote'][:100]}...\"")
        
        print("\n3. KEY EVIDENCE OF CREST FAILURES:")
        for item in evidence['key_quotes'][:5]:
            print(f"   {item['date']}: \"{item['quote'][:100]}...\"")
        
        print("\n\nTIMELINE RECONSTRUCTION:")
        print("-" * 50)
        print("1. Trinity Rose was jointly instructed to survey Plot 34")
        print("2. Crest agreed to pay Trinity Rose £1,300 for the survey")
        print("3. Trinity Rose needed payment confirmation before attending")
        print("4. Crest failed to confirm payment/instruct Trinity Rose directly")
        print("5. This caused delays to the October 11 survey appointment")
        print("6. The survey delays contributed to missing October 31 completion")

def main():
    searcher = TrinityRoseSearcher()
    searcher.search_trinity_rose_issues()

if __name__ == "__main__":
    main()