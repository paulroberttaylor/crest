#!/usr/bin/env python3
"""
Comprehensive search for mortgage-related emails
"""

import chromadb
from chromadb.utils import embedding_functions
import sys
import json

class EmailSearcher:
    def __init__(self):
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails_quick")
        
        # Use same embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get collection
        try:
            self.collection = self.client.get_collection(
                name="emails_quick",
                embedding_function=self.embedding_function
            )
            print(f"Connected to {self.collection.count()} indexed emails\n")
        except:
            print("Error: No indexed emails found.")
            sys.exit(1)
    
    def get_all_emails_in_period(self, start_date, end_date):
        """Get ALL emails in a date range and search manually."""
        # Get a large number of results
        results = self.collection.get(
            limit=2000,
            include=["metadatas", "documents"]
        )
        
        relevant_emails = []
        
        for i, (doc_id, metadata, document) in enumerate(zip(
            results['ids'], 
            results['metadatas'], 
            results['documents']
        )):
            date_str = metadata.get('date', '')
            
            if start_date <= date_str <= end_date:
                # Search for mortgage-related terms
                doc_lower = document.lower()
                
                # Check for various mortgage terms
                if any(term in doc_lower for term in [
                    'mortgage', 'broker', 'rate', 'interest', '1.5%', '1.5 percent',
                    'completion delay', 'financial impact', 'mortgage advisor',
                    'mortgage offer', 'mortgage arrangement', 'lending', 'lender'
                ]):
                    relevant_emails.append({
                        'date': date_str,
                        'from': metadata.get('from', 'Unknown'),
                        'to': metadata.get('to', 'Unknown'),
                        'subject': metadata.get('subject', 'Unknown'),
                        'document': document,
                        'metadata': metadata
                    })
        
        return relevant_emails

def main():
    searcher = EmailSearcher()
    
    print("Performing comprehensive mortgage search...")
    print("Searching ALL emails from 2023 onwards for mortgage references...\n")
    
    # Get all emails from 2023 onwards
    all_mortgage_emails = searcher.get_all_emails_in_period('2023-01-01', '2025-12-31')
    
    print(f"Found {len(all_mortgage_emails)} emails with mortgage-related content\n")
    
    # Sort by date
    all_mortgage_emails.sort(key=lambda x: x['date'])
    
    # Look for specific patterns
    rate_mentions = []
    delay_impacts = []
    june_july_2023 = []
    mortgage_broker_fees = []
    
    for email in all_mortgage_emails:
        doc = email['document']
        doc_lower = doc.lower()
        
        # Check for rate mentions
        if '1.5%' in doc or '1.5 percent' in doc_lower:
            rate_mentions.append(email)
        
        # Check for delay impact discussions
        if 'delay' in doc_lower and 'mortgage' in doc_lower:
            delay_impacts.append(email)
        
        # June-July 2023 emails
        if email['date'].startswith('2023-06') or email['date'].startswith('2023-07'):
            june_july_2023.append(email)
        
        # Mortgage broker fee discussions
        if 'mortgage broker fee' in doc_lower or '£999' in doc or '£1495' in doc:
            mortgage_broker_fees.append(email)
    
    # Display findings
    print("="*80)
    print("MORTGAGE RATE MENTIONS (1.5%)")
    print("="*80)
    
    if rate_mentions:
        for email in rate_mentions[:5]:  # Show first 5
            print(f"\nDate: {email['date']}")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            
            # Find and show context
            lines = email['document'].split('\n')
            for i, line in enumerate(lines):
                if '1.5' in line:
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    print("\nContext:")
                    print("-"*40)
                    print('\n'.join(lines[start:end]))
                    break
    else:
        print("\nNo direct 1.5% rate mentions found")
    
    print("\n" + "="*80)
    print("JUNE-JULY 2023 MORTGAGE DISCUSSIONS")
    print("="*80)
    
    for email in june_july_2023[:10]:  # Show first 10
        if 'mortgage' in email['document'].lower() or 'rate' in email['document'].lower():
            print(f"\nDate: {email['date']}")
            print(f"Subject: {email['subject']}")
            
            # Extract key lines
            lines = email['document'].split('\n')
            relevant_lines = []
            for line in lines[4:]:  # Skip headers
                line_lower = line.lower()
                if any(term in line_lower for term in ['mortgage', 'rate', 'interest', 'delay', 'completion']):
                    relevant_lines.append(line.strip())
            
            if relevant_lines:
                print("Key content:")
                for line in relevant_lines[:3]:
                    if line:
                        print(f"  - {line[:100]}...")
    
    print("\n" + "="*80)
    print("MORTGAGE BROKER FEES AND ARRANGEMENT FEES")
    print("="*80)
    
    for email in mortgage_broker_fees[:5]:
        print(f"\nDate: {email['date']}")
        print(f"Subject: {email['subject']}")
        
        # Show fee mentions
        lines = email['document'].split('\n')
        for line in lines:
            if '£999' in line or '£1495' in line or 'broker fee' in line.lower():
                print(f"  Fee mention: {line.strip()}")
    
    # Save detailed results
    print("\n" + "="*80)
    print("SAVING DETAILED RESULTS...")
    print("="*80)
    
    # Create output with all mortgage emails
    output = {
        'total_mortgage_emails': len(all_mortgage_emails),
        'rate_mentions': len(rate_mentions),
        'delay_impacts': len(delay_impacts),
        'june_july_2023': len(june_july_2023),
        'mortgage_fees': len(mortgage_broker_fees),
        'emails': []
    }
    
    # Add first 20 most relevant emails
    for email in all_mortgage_emails[:20]:
        output['emails'].append({
            'date': email['date'],
            'from': email['from'],
            'to': email['to'],
            'subject': email['subject'],
            'preview': email['document'][:500] + '...' if len(email['document']) > 500 else email['document']
        })
    
    with open('mortgage_email_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nDetailed results saved to mortgage_email_analysis.json")
    print(f"\nSummary:")
    print(f"- Total mortgage-related emails: {len(all_mortgage_emails)}")
    print(f"- Emails mentioning rates: {len(rate_mentions)}")
    print(f"- Emails about delays affecting mortgage: {len(delay_impacts)}")
    print(f"- June-July 2023 mortgage emails: {len(june_july_2023)}")
    print(f"- Mortgage fee discussions: {len(mortgage_broker_fees)}")

if __name__ == "__main__":
    main()