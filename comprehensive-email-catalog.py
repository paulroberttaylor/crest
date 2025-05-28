#!/usr/bin/env python3
"""
Comprehensive email cataloging system for NHOS complaint.
Analyzes every email from Jan 1, 2023 to create a searchable database.
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class EmailCatalog:
    def __init__(self):
        self.emails = []
        self.threads = defaultdict(list)
        self.categories = defaultdict(list)
        self.key_people = defaultdict(list)
        self.issues_timeline = []
        
    def parse_date(self, date_str):
        """Parse ISO date string to datetime object."""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def extract_email_address(self, email_str):
        """Extract email address from string like 'Name <email@domain.com>'"""
        match = re.search(r'<(.+?)>', email_str)
        if match:
            return match.group(1).lower()
        return email_str.lower().strip()
    
    def identify_thread(self, subject):
        """Identify email thread by cleaning subject."""
        # Remove Re:, Fwd:, FW:, etc.
        thread_subject = re.sub(r'^(Re:|RE:|Fwd:|FW:|Fw:|\[EXTERNAL\])+\s*', '', subject).strip()
        thread_subject = re.sub(r'^(Re:|RE:|Fwd:|FW:|Fw:|\[EXTERNAL\])+\s*', '', thread_subject).strip()
        return thread_subject
    
    def categorize_email(self, email):
        """Categorize email by content and context."""
        subject_lower = email['subject'].lower()
        categories = []
        
        # Purchase process
        if any(word in subject_lower for word in ['reservation', 'reserve', 'plot 34']):
            categories.append('purchase_process')
            
        # Legal/Contract
        if any(word in subject_lower for word in ['legal', 'contract', 'solicitor', 'completion']):
            categories.append('legal_contract')
            
        # Complaints
        if 'complaint' in subject_lower:
            if 'acknowledgement' in subject_lower:
                categories.append('complaint_acknowledgement')
            elif 'pathway' in subject_lower:
                categories.append('complaint_pathway')
            elif 'assessment' in subject_lower:
                categories.append('complaint_assessment')
            elif 'final' in subject_lower:
                categories.append('complaint_final')
            else:
                categories.append('complaint_general')
                
        # Defects/Issues
        if any(word in subject_lower for word in ['defect', 'issue', 'problem', 'snag', 'fault']):
            categories.append('defects')
            
        # Specific issues
        if any(word in subject_lower for word in ['render', 'crack']):
            categories.append('render_issue')
            
        if any(word in subject_lower for word in ['garden', 'level']):
            categories.append('garden_levels')
            
        if any(word in subject_lower for word in ['path', 'cycle', 'bridal', 'bridleway', 'access', 'footpath']):
            categories.append('path_access')
            
        if any(word in subject_lower for word in ['trinity', 'rose', 'surveyor', 'survey']):
            categories.append('survey_certification')
            
        # NHBC/Warranty
        if any(word in subject_lower for word in ['nhbc', 'warranty', 'certificate']):
            categories.append('warranty')
            
        # Settlement
        if 'settlement' in subject_lower:
            categories.append('settlement')
            
        # Customer service issues
        if any(word in subject_lower for word in ['urgent', 'chase', 'reminder', 'awaiting', 'delay']):
            categories.append('poor_service')
            
        # NHOS
        if 'nhos' in subject_lower:
            categories.append('nhos_escalation')
            
        return categories
    
    def analyze_email(self, row):
        """Analyze a single email and extract all relevant information."""
        email_data = {
            'date': row['date'],
            'subject': row['subject'],
            'from': row['from'],
            'from_email': self.extract_email_address(row['from']),
            'to': row['to'],
            'cc': row.get('cc', ''),
            'thread': self.identify_thread(row['subject']),
            'categories': [],
            'key_person': None,
            'direction': None,  # 'from_crest', 'to_crest', 'internal'
            'has_attachment': False
        }
        
        # Determine direction
        from_domain = email_data['from_email'].split('@')[-1] if '@' in email_data['from_email'] else ''
        to_emails = [self.extract_email_address(e.strip()) for e in row['to'].split(',')]
        
        if 'crestnicholson.com' in from_domain:
            email_data['direction'] = 'from_crest'
            # Extract key Crest person
            if 'eileen.guihen' in email_data['from_email']:
                email_data['key_person'] = 'Eileen Guihen'
            elif 'lynn.carrington' in email_data['from_email']:
                email_data['key_person'] = 'Lynn Carrington'
            elif 'mark.foyle' in email_data['from_email']:
                email_data['key_person'] = 'Mark Foyle'
            elif 'andy.cook' in email_data['from_email']:
                email_data['key_person'] = 'Andy Cook'
                
        elif any('crestnicholson.com' in e for e in to_emails):
            email_data['direction'] = 'to_crest'
        elif 'nhos.org.uk' in from_domain or any('nhos.org.uk' in e for e in to_emails):
            email_data['direction'] = 'nhos_related'
            
        # Check for attachments (based on subject patterns)
        if any(indicator in row['subject'] for indicator in ['Fwd:', 'FW:', 'attached', 'attachment']):
            email_data['has_attachment'] = True
            
        # Categorize
        email_data['categories'] = self.categorize_email(email_data)
        
        return email_data
    
    def build_catalog(self, csv_path):
        """Build comprehensive catalog from CSV."""
        cutoff_date = datetime(2023, 1, 1, tzinfo=datetime.now().astimezone().tzinfo)
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                email_date = self.parse_date(row['date'])
                if not email_date or email_date < cutoff_date:
                    continue
                    
                # Skip 25 Abbots Road
                if '25 abbots' in row['subject'].lower():
                    continue
                    
                # Analyze email
                email_data = self.analyze_email(row)
                email_data['parsed_date'] = email_date
                
                # Add to catalog
                self.emails.append(email_data)
                
                # Group by thread
                self.threads[email_data['thread']].append(email_data)
                
                # Group by categories
                for cat in email_data['categories']:
                    self.categories[cat].append(email_data)
                    
                # Track key people
                if email_data['key_person']:
                    self.key_people[email_data['key_person']].append(email_data)
        
        # Sort emails by date
        self.emails.sort(key=lambda x: x['parsed_date'])
        
    def generate_reports(self, output_dir):
        """Generate comprehensive reports."""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # 1. Complete email catalog
        catalog_file = output_dir / 'complete_email_catalog.json'
        with open(catalog_file, 'w') as f:
            # Convert datetime objects to strings for JSON
            catalog_data = []
            for email in self.emails:
                email_copy = email.copy()
                email_copy['parsed_date'] = email_copy['parsed_date'].isoformat()
                catalog_data.append(email_copy)
            json.dump(catalog_data, f, indent=2)
        
        # 2. Thread analysis
        thread_file = output_dir / 'email_threads.json'
        thread_summary = {}
        for thread, emails in self.threads.items():
            thread_summary[thread] = {
                'email_count': len(emails),
                'date_range': {
                    'first': emails[0]['date'],
                    'last': emails[-1]['date']
                },
                'participants': list(set(e['from_email'] for e in emails)),
                'categories': list(set(cat for e in emails for cat in e['categories']))
            }
        with open(thread_file, 'w') as f:
            json.dump(thread_summary, f, indent=2)
        
        # 3. Category summary
        category_file = output_dir / 'category_summary.json'
        category_summary = {}
        for cat, emails in self.categories.items():
            category_summary[cat] = {
                'email_count': len(emails),
                'threads': len(set(e['thread'] for e in emails)),
                'key_people': list(set(e['key_person'] for e in emails if e['key_person']))
            }
        with open(category_file, 'w') as f:
            json.dump(category_summary, f, indent=2)
        
        # 4. Key threads report
        key_threads_file = output_dir / 'key_threads_report.md'
        with open(key_threads_file, 'w') as f:
            f.write("# Key Email Threads Analysis\n\n")
            
            # Find most important threads
            important_threads = []
            for thread, emails in self.threads.items():
                importance_score = 0
                
                # Score based on categories
                thread_categories = set(cat for e in emails for cat in e['categories'])
                if any(cat in thread_categories for cat in ['complaint_general', 'complaint_assessment', 'complaint_final']):
                    importance_score += 10
                if 'render_issue' in thread_categories:
                    importance_score += 8
                if 'path_access' in thread_categories:
                    importance_score += 8
                if 'poor_service' in thread_categories:
                    importance_score += 5
                if 'nhos_escalation' in thread_categories:
                    importance_score += 10
                    
                # Score based on length
                importance_score += min(len(emails), 10)
                
                if importance_score > 5:
                    important_threads.append((thread, emails, importance_score))
            
            # Sort by importance
            important_threads.sort(key=lambda x: x[2], reverse=True)
            
            f.write(f"## Found {len(important_threads)} Important Threads\n\n")
            
            for thread, emails, score in important_threads[:20]:  # Top 20
                f.write(f"### Thread: {thread}\n")
                f.write(f"**Importance Score: {score}**\n")
                f.write(f"**Emails: {len(emails)}**\n")
                f.write(f"**Date Range: {emails[0]['date'][:10]} to {emails[-1]['date'][:10]}**\n")
                
                categories = set(cat for e in emails for cat in e['categories'])
                f.write(f"**Categories: {', '.join(categories)}**\n\n")
                
                # Show email flow
                f.write("**Email Flow:**\n")
                for email in emails[:5]:  # First 5 emails
                    date = email['parsed_date'].strftime('%Y-%m-%d %H:%M')
                    direction = email['direction']
                    from_person = email['from'].split('<')[0].strip()
                    f.write(f"- {date} [{direction}] {from_person}: {email['subject']}\n")
                
                if len(emails) > 5:
                    f.write(f"- ... and {len(emails) - 5} more emails\n")
                    
                f.write("\n---\n\n")
        
        # 5. Timeline report
        timeline_file = output_dir / 'categorized_timeline.md'
        with open(timeline_file, 'w') as f:
            f.write("# Categorized Email Timeline\n\n")
            
            current_month = None
            for email in self.emails:
                month = email['parsed_date'].strftime('%Y-%m')
                if month != current_month:
                    current_month = month
                    f.write(f"\n## {email['parsed_date'].strftime('%B %Y')}\n\n")
                
                date = email['parsed_date'].strftime('%d')
                categories = ', '.join(email['categories']) if email['categories'] else 'uncategorized'
                direction = email['direction'] or 'unknown'
                
                f.write(f"- **{date}** [{direction}] {email['subject']}\n")
                f.write(f"  - Categories: {categories}\n")
                if email['key_person']:
                    f.write(f"  - Key person: {email['key_person']}\n")
        
        return {
            'total_emails': len(self.emails),
            'total_threads': len(self.threads),
            'important_threads': len(important_threads),
            'categories_found': list(self.categories.keys())
        }

def main():
    print("Building comprehensive email catalog...")
    
    catalog = EmailCatalog()
    catalog.build_catalog('email_analysis/email_summary.csv')
    
    print(f"Analyzed {len(catalog.emails)} emails")
    print(f"Found {len(catalog.threads)} unique threads")
    print(f"Identified {len(catalog.categories)} categories")
    
    results = catalog.generate_reports('email_catalog')
    
    print("\n=== Catalog Complete ===")
    print(f"Total emails analyzed: {results['total_emails']}")
    print(f"Email threads identified: {results['total_threads']}")
    print(f"Important threads found: {results['important_threads']}")
    print(f"\nCategories found: {', '.join(results['categories_found'])}")
    
    print("\n=== Output Files ===")
    print("email_catalog/complete_email_catalog.json - Full searchable database")
    print("email_catalog/email_threads.json - Thread analysis")
    print("email_catalog/category_summary.json - Category breakdown")
    print("email_catalog/key_threads_report.md - Important threads to investigate")
    print("email_catalog/categorized_timeline.md - Complete timeline with categories")

if __name__ == "__main__":
    main()