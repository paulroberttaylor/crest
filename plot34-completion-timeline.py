#!/usr/bin/env python3
"""
Extract detailed timeline of Plot 34 completion date changes
"""

import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import re

class CompletionTimelineAnalyzer:
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
        print(f"Analyzing {self.collection.count()} emails for completion date changes...\n")
    
    def search_completion_dates(self):
        """Search for all mentions of completion dates and timeline changes."""
        
        # Search terms related to completion dates
        search_queries = [
            "plot 34 completion date June July",
            "plot 34 ready September October", 
            "plot 34 completion when available",
            "plot 34 exchange contract delay",
            "10 colt view completion date",
            "adrian sims plot 34",
            "site manager June July",
            "completion moved changed delayed",
            "plot 34 build schedule timeline"
        ]
        
        all_results = []
        seen_ids = set()
        
        for query in search_queries:
            results = self.collection.query(
                query_texts=[query],
                n_results=30
            )
            
            for i, (doc_id, metadata, document, distance) in enumerate(zip(
                results['ids'][0], 
                results['metadatas'][0], 
                results['documents'][0],
                results['distances'][0]
            )):
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    
                    # Check if relevant
                    doc_lower = document.lower()
                    if any(term in doc_lower for term in ['complet', 'exchange', 'june', 'july', 'september', 'october', 'november', 'december', 'ready', 'delay', 'plot 34', '10 colt']):
                        all_results.append({
                            'date': metadata.get('date', ''),
                            'from': metadata.get('from', ''),
                            'to': metadata.get('to', ''),
                            'subject': metadata.get('subject', ''),
                            'document': document,
                            'score': 1 - distance
                        })
        
        # Sort by date
        all_results.sort(key=lambda x: x['date'])
        
        return all_results
    
    def extract_completion_mentions(self, document):
        """Extract mentions of completion dates from document."""
        mentions = []
        doc_lower = document.lower()
        lines = document.split('\n')
        
        # Look for month mentions
        months = ['june', 'july', 'august', 'september', 'october', 'november', 'december']
        date_patterns = [
            r'ready (?:in|by) (\w+)',
            r'complete (?:in|by|on) (\w+)',
            r'completion (?:in|by|on|date) (\w+)',
            r'available (?:in|by) (\w+)',
            r'(\w+) completion',
            r'exchange (?:in|by|on) (\w+)',
            r'move (?:in|by) (\w+)'
        ]
        
        for line in lines:
            line_lower = line.lower()
            
            # Check for month mentions with context
            for month in months:
                if month in line_lower:
                    # Extract surrounding context
                    for pattern in date_patterns:
                        match = re.search(pattern, line_lower)
                        if match:
                            mentions.append(line.strip())
                            break
                    else:
                        # General month mention
                        if any(word in line_lower for word in ['complet', 'ready', 'exchange', 'delay', 'move']):
                            mentions.append(line.strip())
            
            # Check for specific date mentions
            if re.search(r'\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+202\d', line):
                mentions.append(line.strip())
            
        return mentions
    
    def generate_timeline_document(self):
        """Generate detailed timeline document."""
        
        results = self.search_completion_dates()
        
        # Create timeline document
        with open('plot34_completion_timeline.md', 'w') as f:
            f.write("# Plot 34 (10 Colt View) - Completion Date Timeline\n\n")
            f.write("## Summary of Completion Date Changes\n\n")
            f.write("This document tracks how the completion date for Plot 34 changed throughout 2023,\n")
            f.write("from initial estimates to actual completion.\n\n")
            f.write("---\n\n")
            
            # Group by month
            current_month = None
            
            for result in results:
                email_date = result['date']
                if not email_date:
                    continue
                
                # Parse date
                try:
                    dt = datetime.fromisoformat(email_date.replace('Z', '+00:00'))
                    month_year = dt.strftime('%B %Y')
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    continue
                
                # Extract completion mentions
                mentions = self.extract_completion_mentions(result['document'])
                if not mentions:
                    continue
                
                # New month header
                if month_year != current_month:
                    current_month = month_year
                    f.write(f"\n## {month_year}\n\n")
                
                # Write email details
                f.write(f"### {date_str}\n")
                f.write(f"**From:** {result['from']}\n")
                f.write(f"**To:** {result['to']}\n")
                f.write(f"**Subject:** {result['subject']}\n\n")
                
                # Write relevant mentions
                if mentions:
                    f.write("**Key mentions:**\n")
                    for mention in mentions[:3]:  # Limit to 3 per email
                        f.write(f"- {mention}\n")
                
                f.write("\n---\n")
            
            # Add summary section
            f.write("\n## Key Timeline Summary\n\n")
            f.write("Based on the email analysis:\n\n")
            f.write("1. **Initial Estimate (Site Manager)**: June/July 2023\n")
            f.write("2. **Revised to**: September/October 2023\n")
            f.write("3. **Further delayed to**: October 31, 2023\n")
            f.write("4. **Not ready**: October 24, 2023 (solicitor confirms)\n")
            f.write("5. **Final completion**: December 18, 2023\n\n")
            f.write("**Total delay**: Approximately 6 months from initial estimate\n")
        
        print("Timeline document created: plot34_completion_timeline.md")
    
    def search_adrian_sims_emails(self):
        """Specifically search for Adrian Sims emails about Plot 34."""
        
        print("\nSearching for Adrian Sims emails about Plot 34 timeline...\n")
        
        results = self.collection.query(
            query_texts=["Adrian Sims plot 34 completion date excuse reason"],
            n_results=20
        )
        
        adrian_emails = []
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            from_addr = metadata.get('from', '').lower()
            if 'adrian' in from_addr or 'adrian.sims' in from_addr:
                adrian_emails.append({
                    'date': metadata.get('date', ''),
                    'subject': metadata.get('subject', ''),
                    'document': document
                })
        
        if adrian_emails:
            print("Found Adrian Sims emails:")
            for email in adrian_emails:
                print(f"\nDate: {email['date']}")
                print(f"Subject: {email['subject']}")
                # Look for excuse/reason
                lines = email['document'].split('\n')
                for line in lines:
                    if any(word in line.lower() for word in ['reason', 'because', 'due to', 'delay', 'unfortunately']):
                        print(f"Content: {line.strip()}")

def main():
    analyzer = CompletionTimelineAnalyzer()
    analyzer.generate_timeline_document()
    analyzer.search_adrian_sims_emails()

if __name__ == "__main__":
    main()