#!/usr/bin/env python3
"""
Search for specific completion delay evidence from October-December 2023
"""

import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
from collections import defaultdict

class CompletionDelayAnalyzer:
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
    
    def search_by_date_and_topic(self, start_date: str, end_date: str, topics: list, n_results: int = 200):
        """Search for emails within date range about specific topics."""
        all_results = []
        seen_ids = set()
        
        for topic in topics:
            print(f"Searching for: {topic}")
            results = self.collection.query(
                query_texts=[topic],
                n_results=n_results
            )
            
            for i, (doc_id, metadata, document, distance) in enumerate(zip(
                results['ids'][0], 
                results['metadatas'][0], 
                results['documents'][0],
                results['distances'][0]
            )):
                date = metadata.get('date', '')
                if start_date <= date <= end_date:
                    email_key = f"{date}_{metadata.get('subject', '')}"
                    if email_key not in seen_ids:
                        seen_ids.add(email_key)
                        all_results.append({
                            'date': date,
                            'subject': metadata.get('subject', ''),
                            'from': metadata.get('from', ''),
                            'to': metadata.get('to', ''),
                            'document': document,
                            'score': 1 - distance
                        })
        
        return sorted(all_results, key=lambda x: x['date'])
    
    def analyze_completion_delays(self):
        """Analyze completion delay evidence from October-December 2023."""
        
        # Key search terms
        topics = [
            "Trinity Rose survey access property",
            "October 31 completion ready complete",
            "updated contract amendments replies enquiries",
            "redemption statement delay",
            "consent proposed works",
            "I do not believe we will be ready to complete",
            "exchange contracts completion date",
            "URGENT 10 Colt View delay",
            "Hannah Rafferty Bramsdon Childs",
            "Natalie Haigh Crest Nicholson",
            "survey access appointment Trinity",
            "contract not ready documentation missing"
        ]
        
        emails = self.search_by_date_and_topic('2023-10-01', '2023-12-31', topics, n_results=150)
        
        print(f"\nFound {len(emails)} relevant emails from October-December 2023\n")
        print("=" * 100)
        
        # Group by key events
        key_events = {
            'october_24': [],
            'trinity_rose': [],
            'contract_issues': [],
            'november_delays': [],
            'december_urgent': [],
            'completion_obstacles': []
        }
        
        for email in emails:
            doc_lower = email['document'].lower()
            date = email['date'][:10] if email['date'] else 'Unknown'
            
            # October 24 critical email
            if '2023-10-24' in email['date'] and 'i do not believe we will be ready' in doc_lower:
                key_events['october_24'].append(email)
            
            # Trinity Rose access
            if 'trinity rose' in doc_lower and any(term in doc_lower for term in ['survey', 'access', 'appointment']):
                key_events['trinity_rose'].append(email)
            
            # Contract issues
            if any(term in doc_lower for term in ['updated contract', 'contract amendment', 'replies to enquiries', 'full replies']):
                key_events['contract_issues'].append(email)
            
            # November delays
            if '2023-11' in email['date'] and any(term in doc_lower for term in ['delay', 'waiting', 'chasing', 'outstanding']):
                key_events['november_delays'].append(email)
            
            # December urgent emails
            if '2023-12' in email['date'] and 'urgent' in doc_lower:
                key_events['december_urgent'].append(email)
            
            # General completion obstacles
            if any(term in doc_lower for term in ['redemption statement', 'consent for proposed works', 'cannot complete', 'not ready']):
                key_events['completion_obstacles'].append(email)
        
        # Print findings
        print("\n1. OCTOBER 24, 2023 - CRITICAL DATE")
        print("-" * 50)
        for email in key_events['october_24']:
            self.print_email_detail(email, highlight_terms=['i do not believe we will be ready', 'october 31', 'complete'])
        
        print("\n2. TRINITY ROSE SURVEY ACCESS ISSUES")
        print("-" * 50)
        for email in key_events['trinity_rose'][:5]:  # First 5
            self.print_email_detail(email, highlight_terms=['trinity rose', 'survey', 'access', 'appointment'])
        
        print("\n3. CONTRACT DOCUMENTATION ISSUES")
        print("-" * 50)
        for email in key_events['contract_issues'][:5]:
            self.print_email_detail(email, highlight_terms=['contract', 'amendment', 'enquiries', 'documentation'])
        
        print("\n4. NOVEMBER DELAYS - WHAT HAPPENED?")
        print("-" * 50)
        for email in key_events['november_delays'][:5]:
            self.print_email_detail(email, highlight_terms=['delay', 'waiting', 'chasing', 'outstanding'])
        
        print("\n5. DECEMBER URGENT EXCHANGES")
        print("-" * 50)
        for email in key_events['december_urgent'][:5]:
            self.print_email_detail(email, highlight_terms=['urgent', 'exchange', 'complete', 'today'])
        
        print("\n6. SPECIFIC COMPLETION OBSTACLES")
        print("-" * 50)
        obstacles = defaultdict(list)
        for email in key_events['completion_obstacles']:
            doc_lower = email['document'].lower()
            if 'redemption statement' in doc_lower:
                obstacles['Redemption Statement'].append(email)
            if 'consent for proposed works' in doc_lower or 'consent to proposed works' in doc_lower:
                obstacles['Consent for Works'].append(email)
            if 'replies to enquiries' in doc_lower or 'full replies' in doc_lower:
                obstacles['Enquiries Not Answered'].append(email)
            if 'updated contract' in doc_lower or 'contract amendment' in doc_lower:
                obstacles['Contract Amendments'].append(email)
        
        for obstacle_type, emails in obstacles.items():
            if emails:
                print(f"\n{obstacle_type} ({len(emails)} instances):")
                for email in emails[:2]:  # First 2 of each type
                    print(f"  - {email['date'][:10]}: {email['subject'][:60]}...")
                    # Find relevant quote
                    lines = email['document'].split('\n')
                    for line in lines:
                        if obstacle_type.lower() in line.lower():
                            print(f"    \"{line.strip()[:120]}...\"")
                            break
        
        # Timeline summary
        print("\n\nTIMELINE OF DELAYS AND OBSTACLES:")
        print("=" * 50)
        
        timeline_events = []
        for email in emails:
            doc_lower = email['document'].lower()
            date = email['date'][:10]
            
            if 'i do not believe we will be ready' in doc_lower:
                timeline_events.append((date, "❌ Solicitor confirms NOT ready for Oct 31 completion"))
            elif 'trinity rose' in doc_lower and 'access' in doc_lower:
                timeline_events.append((date, "🏠 Trinity Rose access issue mentioned"))
            elif 'still waiting' in doc_lower and 'redemption' in doc_lower:
                timeline_events.append((date, "⏰ Still waiting for redemption statement"))
            elif 'consent for proposed works' in doc_lower:
                timeline_events.append((date, "📋 Consent for proposed works outstanding"))
            elif 'exchange today' in doc_lower or 'exchanging today' in doc_lower:
                timeline_events.append((date, "📝 Attempting exchange"))
            elif 'urgent' in email['subject'].upper():
                timeline_events.append((date, "🚨 URGENT email sent"))
        
        # Remove duplicates and sort
        timeline_events = list(set(timeline_events))
        timeline_events.sort()
        
        for date, event in timeline_events:
            print(f"{date}: {event}")
    
    def print_email_detail(self, email, highlight_terms=[]):
        """Print detailed email information with highlighted quotes."""
        print(f"\nDate: {email['date'][:16]}")
        print(f"From: {email['from']}")
        print(f"To: {email['to']}")
        print(f"Subject: {email['subject']}")
        print("Key quotes:")
        
        lines = email['document'].split('\n')
        quotes_found = 0
        for line in lines[4:]:  # Skip headers
            line_lower = line.lower()
            if any(term.lower() in line_lower for term in highlight_terms):
                quote = line.strip()
                if quote and len(quote) > 20:  # Meaningful content
                    print(f"  \"{quote[:200]}...\"")
                    quotes_found += 1
                    if quotes_found >= 3:  # Max 3 quotes per email
                        break

def main():
    analyzer = CompletionDelayAnalyzer()
    analyzer.analyze_completion_delays()

if __name__ == "__main__":
    main()