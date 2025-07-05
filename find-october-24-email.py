#!/usr/bin/env python3
"""
Find the October 24, 2023 email from Hannah Rafferty
"""

import chromadb
from chromadb.utils import embedding_functions

class October24Finder:
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
    
    def find_october_24(self):
        """Find the specific October 24 email."""
        
        print("SEARCHING FOR OCTOBER 24, 2023 EMAIL")
        print("=" * 80)
        
        # Multiple search strategies
        searches = [
            "Hannah Rafferty URGENT October 24 2023",
            "I do not believe we will be ready to complete",
            "not ready complete 31st October 2023",
            "updated contract full replies enquiries October"
        ]
        
        found_emails = []
        
        for query in searches:
            print(f"\nTrying search: {query}")
            results = self.collection.query(
                query_texts=[query],
                n_results=50
            )
            
            for i, (doc_id, metadata, document, distance) in enumerate(zip(
                results['ids'][0], 
                results['metadatas'][0], 
                results['documents'][0],
                results['distances'][0]
            )):
                date = metadata.get('date', '')
                from_addr = metadata.get('from', '')
                
                # Look for emails around October 24, 2023
                if '2023-10' in date:
                    doc_lower = document.lower()
                    
                    # Check if this might be THE email
                    if any([
                        'i do not believe we will be ready' in doc_lower,
                        'not ready to complete' in doc_lower,
                        '31st october' in doc_lower and 'ready' in doc_lower,
                        'updated contract' in doc_lower and 'enquiries' in doc_lower
                    ]):
                        found_emails.append({
                            'date': date,
                            'from': from_addr,
                            'to': metadata.get('to', ''),
                            'subject': metadata.get('subject', ''),
                            'document': document,
                            'score': 1 - distance
                        })
        
        # Remove duplicates and sort
        seen = set()
        unique_emails = []
        for email in found_emails:
            key = f"{email['date']}-{email['subject']}"
            if key not in seen:
                seen.add(key)
                unique_emails.append(email)
        
        unique_emails.sort(key=lambda x: x['date'])
        
        print(f"\n\nFOUND {len(unique_emails)} POTENTIAL MATCHES:")
        print("-" * 80)
        
        # Display each potential match
        for email in unique_emails:
            print(f"\nDate: {email['date']}")
            print(f"From: {email['from']}")
            print(f"To: {email['to']}")
            print(f"Subject: {email['subject']}")
            
            # Look for the key quote
            lines = email['document'].split('\n')
            found_key_quote = False
            
            for line in lines:
                line_lower = line.lower()
                if any([
                    'i do not believe we will be ready' in line_lower,
                    'not ready to complete' in line_lower,
                    '31st october' in line_lower and not any(word in line_lower for word in ['ready', 'complete']),
                    'updated contract' in line_lower
                ]):
                    print(f"KEY QUOTE: \"{line.strip()}\"")
                    found_key_quote = True
            
            if not found_key_quote:
                # Show some content anyway
                for line in lines[5:10]:
                    if len(line.strip()) > 40:
                        print(f"Content: \"{line.strip()[:100]}...\"")
                        break
        
        # Now search specifically for emails TO Hannah Rafferty around that time
        print("\n\nSEARCHING FOR EMAILS TO/FROM HANNAH RAFFERTY IN OCTOBER 2023:")
        print("-" * 80)
        
        results = self.collection.query(
            query_texts=["Hannah Rafferty October 2023 completion"],
            n_results=100
        )
        
        hannah_october = []
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            date = metadata.get('date', '')
            from_addr = metadata.get('from', '').lower()
            to_addr = metadata.get('to', '').lower()
            
            if '2023-10' in date and ('hannah' in from_addr or 'hannah' in to_addr or 'hr@bramsdon' in from_addr):
                hannah_october.append({
                    'date': date,
                    'from': metadata.get('from', ''),
                    'to': metadata.get('to', ''),
                    'subject': metadata.get('subject', ''),
                    'document': document
                })
        
        # Sort by date
        hannah_october.sort(key=lambda x: x['date'])
        
        print(f"\nFound {len(hannah_october)} October 2023 emails involving Hannah Rafferty:")
        
        for email in hannah_october:
            if '24' in email['date'] or '23' in email['date'] or '25' in email['date']:
                print(f"\n{email['date'][:16]}")
                print(f"From: {email['from'].split('<')[0].strip()}")
                print(f"To: {email['to'].split('<')[0].strip()}")
                print(f"Subject: {email['subject']}")
                
                # Check for key content
                doc_lower = email['document'].lower()
                if 'ready' in doc_lower or 'complete' in doc_lower or 'october' in doc_lower:
                    lines = email['document'].split('\n')
                    for line in lines:
                        if any(word in line.lower() for word in ['ready', 'complete', 'october', 'contract']):
                            if len(line.strip()) > 20:
                                print(f"  \"{line.strip()[:120]}...\"")
                                break

def main():
    finder = October24Finder()
    finder.find_october_24()

if __name__ == "__main__":
    main()