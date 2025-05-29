#!/usr/bin/env python3
"""
Create detailed Plot 34 completion timeline with all date changes
"""

import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import re

class DetailedTimelineBuilder:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chromadb_emails_quick")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_collection(
            name="emails_quick",
            embedding_function=self.embedding_function
        )
    
    def search_all_mentions(self):
        """Search for all mentions of completion dates."""
        
        # Cast a wide net
        searches = [
            # Early mentions
            "plot 34 June July site manager",
            "plot 34 when will ready building",
            "September October plot 34",
            "Adrian Sims plot 34",
            
            # Contract and delays
            "memorandum agreement plot 34",
            "reservation plot 34 completion",
            "contract plot 34 exchange delay",
            "October 31 completion",
            "not ready complete October",
            
            # December completion
            "December completion 10 colt",
            "exchange December plot 34",
            "completion 18 December"
        ]
        
        all_emails = {}
        
        for search in searches:
            results = self.collection.query(
                query_texts=[search],
                n_results=20
            )
            
            for i, (doc_id, meta, doc, dist) in enumerate(zip(
                results['ids'][0],
                results['metadatas'][0], 
                results['documents'][0],
                results['distances'][0]
            )):
                # Use date as key to avoid duplicates
                date_key = meta.get('date', '')
                if date_key and date_key not in all_emails:
                    all_emails[date_key] = {
                        'date': date_key,
                        'from': meta.get('from', ''),
                        'to': meta.get('to', ''),
                        'subject': meta.get('subject', ''),
                        'content': doc
                    }
        
        # Sort by date
        sorted_emails = sorted(all_emails.values(), key=lambda x: x['date'])
        
        return sorted_emails
    
    def build_timeline(self):
        """Build comprehensive timeline document."""
        
        emails = self.search_all_mentions()
        
        timeline_entries = []
        
        for email in emails:
            content = email['content'].lower()
            
            # Skip if not relevant
            if not any(term in content for term in ['plot 34', '10 colt', 'complet', 'exchange', 'june', 'july', 'september', 'october', 'november', 'december']):
                continue
            
            # Parse date
            try:
                dt = datetime.fromisoformat(email['date'].replace('Z', '+00:00'))
            except:
                continue
            
            # Extract key information
            entry = {
                'datetime': dt,
                'date_str': dt.strftime('%Y-%m-%d %H:%M'),
                'from': email['from'],
                'to': email['to'],
                'subject': email['subject'],
                'key_points': []
            }
            
            # Look for key phrases
            lines = email['content'].split('\n')
            for line in lines:
                line_lower = line.lower()
                
                # June/July mentions
                if ('june' in line_lower or 'july' in line_lower) and ('plot 34' in line_lower or 'ready' in line_lower or 'complet' in line_lower):
                    entry['key_points'].append(f"June/July mention: {line.strip()[:200]}")
                
                # September/October mentions  
                elif ('september' in line_lower or 'october' in line_lower) and ('plot 34' in line_lower or 'ready' in line_lower or 'complet' in line_lower):
                    entry['key_points'].append(f"Sept/Oct mention: {line.strip()[:200]}")
                
                # Delay mentions
                elif 'delay' in line_lower and ('plot 34' in line_lower or 'complet' in line_lower):
                    entry['key_points'].append(f"Delay: {line.strip()[:200]}")
                
                # Not ready mentions
                elif 'not ready' in line_lower or 'cannot complete' in line_lower:
                    entry['key_points'].append(f"Not ready: {line.strip()[:200]}")
                
                # Exchange/completion mentions
                elif ('exchange' in line_lower or 'complet' in line_lower) and any(month in line_lower for month in ['october', 'november', 'december']):
                    entry['key_points'].append(f"Exchange/completion: {line.strip()[:200]}")
            
            if entry['key_points']:
                timeline_entries.append(entry)
        
        # Write timeline document
        with open('plot34_detailed_timeline.md', 'w') as f:
            f.write("# Plot 34 (10 Colt View) - Detailed Completion Timeline\n\n")
            f.write("**Property:** Plot 34, Albany Wood (10 Colt View, Bishops Waltham)\n")
            f.write("**Timeline:** 2023\n\n")
            f.write("---\n\n")
            
            current_month = None
            
            for entry in timeline_entries:
                month = entry['datetime'].strftime('%B %Y')
                
                if month != current_month:
                    current_month = month
                    f.write(f"\n## {month}\n\n")
                
                f.write(f"### {entry['date_str']}\n")
                f.write(f"**From:** {entry['from']}\n")
                f.write(f"**To:** {entry['to']}\n")
                f.write(f"**Subject:** {entry['subject']}\n\n")
                
                for point in entry['key_points']:
                    f.write(f"- {point}\n")
                
                f.write("\n---\n")
            
            # Add summary
            f.write("\n# Timeline Summary\n\n")
            f.write("## Completion Date Changes:\n\n")
            f.write("1. **Initial indication from site**: June/July 2023\n")
            f.write("2. **Revised estimate**: September/October 2023\n")
            f.write("3. **Target date set**: October 31, 2023\n")
            f.write("4. **October 24, 2023**: Solicitor confirms \"not ready to complete\"\n")
            f.write("5. **December 2023**: Multiple attempts to exchange\n")
            f.write("6. **December 18, 2023**: Actual completion\n\n")
            f.write("## Key Issues:\n\n")
            f.write("- Contract not provided in time\n")
            f.write("- Enquiry responses delayed\n")
            f.write("- Multiple contract amendments needed\n")
            f.write("- Fence/boundary issues\n")
            f.write("- Total delay: ~6 months from initial estimate\n")
        
        print(f"Created detailed timeline with {len(timeline_entries)} entries")
        print("Saved to: plot34_detailed_timeline.md")

def main():
    builder = DetailedTimelineBuilder()
    builder.build_timeline()

if __name__ == "__main__":
    main()