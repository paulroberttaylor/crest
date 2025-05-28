#!/usr/bin/env python3
"""
Comprehensive analysis of ALL email threads from Jan 1, 2023.
Includes both Paul and Jade's emails.
Analyzes full conversations to extract all evidence.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class ComprehensiveAnalyzer:
    def __init__(self):
        self.threads_by_subject = defaultdict(list)
        self.jade_emails = []
        self.paul_emails = []
        self.all_evidence = {
            'communication_issues': [],
            'promises_made': [],
            'issues_raised': [],
            'crest_responses': [],
            'escalations': [],
            'key_people': defaultdict(list),
            'thread_summaries': {}
        }
        
    def parse_date(self, date_str):
        """Parse ISO date string to datetime object."""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def extract_email_address(self, email_str):
        """Extract email address from string."""
        import re
        match = re.search(r'<(.+?)>', email_str)
        if match:
            return match.group(1).lower()
        return email_str.lower().strip()
    
    def identify_sender_type(self, email):
        """Identify if sender is Paul, Jade, Crest, or other."""
        from_addr = self.extract_email_address(email['from'])
        
        if 'paulroberttaylor' in from_addr:
            return 'paul'
        elif 'jade.millington' in from_addr:
            return 'jade'
        elif 'crestnicholson.com' in from_addr:
            return 'crest'
        elif 'nhos.org.uk' in from_addr:
            return 'nhos'
        elif 'bramsdonandchilds.com' in from_addr:
            return 'solicitor'
        else:
            return 'other'
    
    def analyze_thread(self, thread_emails):
        """Analyze a complete email thread for evidence."""
        if not thread_emails:
            return None
            
        # Sort by date
        thread_emails.sort(key=lambda x: x['parsed_date'])
        
        thread_analysis = {
            'subject': thread_emails[0]['thread'],
            'date_range': {
                'start': thread_emails[0]['date'],
                'end': thread_emails[-1]['date']
            },
            'email_count': len(thread_emails),
            'participants': {},
            'customer_emails': 0,
            'crest_responses': 0,
            'response_times': [],
            'issues_mentioned': [],
            'evidence_points': []
        }
        
        # Count participants
        for email in thread_emails:
            sender_type = self.identify_sender_type(email)
            thread_analysis['participants'][sender_type] = thread_analysis['participants'].get(sender_type, 0) + 1
            
            if sender_type in ['paul', 'jade']:
                thread_analysis['customer_emails'] += 1
            elif sender_type == 'crest':
                thread_analysis['crest_responses'] += 1
        
        # Analyze response times
        for i in range(len(thread_emails) - 1):
            email1 = thread_emails[i]
            email2 = thread_emails[i + 1]
            
            sender1 = self.identify_sender_type(email1)
            sender2 = self.identify_sender_type(email2)
            
            # Customer email followed by Crest response
            if sender1 in ['paul', 'jade'] and sender2 == 'crest':
                days = (email2['parsed_date'] - email1['parsed_date']).days
                thread_analysis['response_times'].append({
                    'days': days,
                    'customer_email': email1['subject'],
                    'date': email1['date']
                })
                
                if days > 3:  # Slow response
                    thread_analysis['evidence_points'].append(
                        f"Slow response: {days} days to respond to customer email on {email1['date'][:10]}"
                    )
        
        # Check for multiple customer emails without response
        consecutive_customer = 0
        for email in thread_emails:
            sender = self.identify_sender_type(email)
            if sender in ['paul', 'jade']:
                consecutive_customer += 1
            else:
                if consecutive_customer > 2:
                    thread_analysis['evidence_points'].append(
                        f"Customer had to send {consecutive_customer} emails before getting a response"
                    )
                consecutive_customer = 0
        
        # Extract key issues from subject
        subject_lower = thread_analysis['subject'].lower()
        if 'urgent' in subject_lower:
            thread_analysis['issues_mentioned'].append('urgent_matter')
            thread_analysis['evidence_points'].append("Marked as URGENT by customer")
            
        if 'contract' in subject_lower:
            thread_analysis['issues_mentioned'].append('contract_issues')
            
        if any(word in subject_lower for word in ['defect', 'snag', 'issue', 'problem']):
            thread_analysis['issues_mentioned'].append('quality_issues')
            
        if 'completion' in subject_lower:
            thread_analysis['issues_mentioned'].append('completion_issues')
            
        if 'complaint' in subject_lower:
            thread_analysis['issues_mentioned'].append('formal_complaint')
            
        return thread_analysis
    
    def extract_all_evidence(self, emails):
        """Extract evidence from all emails."""
        # First, group by thread
        for email in emails:
            thread = email['thread']
            self.threads_by_subject[thread].append(email)
            
            # Track Jade's emails specifically
            if 'jade.millington' in email['from'].lower():
                self.jade_emails.append(email)
            elif 'paulroberttaylor' in email['from'].lower():
                self.paul_emails.append(email)
        
        # Analyze each thread
        for thread, thread_emails in self.threads_by_subject.items():
            analysis = self.analyze_thread(thread_emails)
            if analysis:
                self.all_evidence['thread_summaries'][thread] = analysis
                
                # Extract key evidence
                if analysis['evidence_points']:
                    for point in analysis['evidence_points']:
                        self.all_evidence['communication_issues'].append({
                            'thread': thread,
                            'evidence': point,
                            'email_count': analysis['email_count']
                        })
                        
                # Track slow responses
                for response in analysis['response_times']:
                    if response['days'] > 3:
                        self.all_evidence['communication_issues'].append({
                            'thread': thread,
                            'evidence': f"{response['days']} day response time",
                            'date': response['date']
                        })
                        
                # Track where customers had to chase
                if analysis['customer_emails'] > analysis['crest_responses'] * 1.5:
                    self.all_evidence['communication_issues'].append({
                        'thread': thread,
                        'evidence': f"Customer sent {analysis['customer_emails']} emails but only got {analysis['crest_responses']} responses",
                        'email_count': analysis['email_count']
                    })
    
    def generate_comprehensive_report(self, output_dir):
        """Generate comprehensive analysis report."""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Save raw data
        data_file = output_dir / 'comprehensive_thread_data.json'
        with open(data_file, 'w') as f:
            # Convert for JSON serialization
            data = {
                'total_threads': len(self.threads_by_subject),
                'jade_email_count': len(self.jade_emails),
                'paul_email_count': len(self.paul_emails),
                'evidence': self.all_evidence
            }
            json.dump(data, f, indent=2)
        
        # Generate report
        report_file = output_dir / 'comprehensive_analysis_report.md'
        with open(report_file, 'w') as f:
            f.write("# Comprehensive Email Thread Analysis\n\n")
            f.write("*Analysis of ALL emails from Jan 1, 2023 including both Paul and Jade Taylor*\n\n")
            
            f.write("## Summary Statistics\n\n")
            f.write(f"- Total email threads analyzed: {len(self.threads_by_subject)}\n")
            f.write(f"- Emails from Paul: {len(self.paul_emails)}\n")
            f.write(f"- Emails from Jade: {len(self.jade_emails)}\n")
            f.write(f"- Total customer emails: {len(self.paul_emails) + len(self.jade_emails)}\n\n")
            
            # Jade's involvement
            if self.jade_emails:
                f.write("## Jade's Email Involvement\n\n")
                f.write(f"Jade sent {len(self.jade_emails)} emails across the following threads:\n\n")
                
                jade_threads = defaultdict(int)
                for email in self.jade_emails:
                    jade_threads[email['thread']] += 1
                
                for thread, count in sorted(jade_threads.items(), key=lambda x: x[1], reverse=True)[:10]:
                    f.write(f"- **{thread}**: {count} emails\n")
                f.write("\n")
            
            # Most problematic threads
            f.write("## Most Problematic Threads\n\n")
            f.write("*Threads with most evidence of poor treatment*\n\n")
            
            problem_threads = []
            for thread, analysis in self.all_evidence['thread_summaries'].items():
                score = 0
                score += len(analysis['evidence_points']) * 2
                score += sum(1 for rt in analysis['response_times'] if rt['days'] > 3)
                if analysis['customer_emails'] > analysis['crest_responses']:
                    score += (analysis['customer_emails'] - analysis['crest_responses'])
                if 'urgent_matter' in analysis['issues_mentioned']:
                    score += 5
                    
                if score > 0:
                    problem_threads.append((thread, analysis, score))
            
            problem_threads.sort(key=lambda x: x[2], reverse=True)
            
            for thread, analysis, score in problem_threads[:15]:
                f.write(f"### {thread}\n")
                f.write(f"**Problem Score: {score}**\n")
                f.write(f"- Emails: {analysis['email_count']} ")
                f.write(f"({analysis['customer_emails']} from customer, {analysis['crest_responses']} from Crest)\n")
                f.write(f"- Date range: {analysis['date_range']['start'][:10]} to {analysis['date_range']['end'][:10]}\n")
                
                if analysis['evidence_points']:
                    f.write("- **Evidence:**\n")
                    for point in analysis['evidence_points']:
                        f.write(f"  - {point}\n")
                        
                avg_response = sum(rt['days'] for rt in analysis['response_times']) / len(analysis['response_times']) if analysis['response_times'] else 0
                if avg_response > 0:
                    f.write(f"- **Average response time: {avg_response:.1f} days**\n")
                    
                f.write("\n")
            
            # Communication failures
            f.write("## Evidence of Communication Failures\n\n")
            f.write(f"Found {len(self.all_evidence['communication_issues'])} instances:\n\n")
            
            # Group by type
            slow_responses = [e for e in self.all_evidence['communication_issues'] if 'day response time' in e['evidence']]
            had_to_chase = [e for e in self.all_evidence['communication_issues'] if 'Customer sent' in e['evidence']]
            urgent_ignored = [e for e in self.all_evidence['communication_issues'] if 'URGENT' in e['evidence']]
            
            if slow_responses:
                f.write(f"### Slow Responses ({len(slow_responses)} instances)\n")
                for item in slow_responses[:10]:
                    f.write(f"- {item['evidence']} in thread: {item['thread']}\n")
                f.write("\n")
                
            if had_to_chase:
                f.write(f"### Customer Had to Chase ({len(had_to_chase)} instances)\n")
                for item in had_to_chase[:10]:
                    f.write(f"- {item['evidence']}\n")
                f.write("\n")
                
            if urgent_ignored:
                f.write(f"### Urgent Matters ({len(urgent_ignored)} instances)\n")
                for item in urgent_ignored[:5]:
                    f.write(f"- Thread: {item['thread']}\n")
                f.write("\n")
            
            # Threads to investigate further
            f.write("## Priority Threads for PDF Extraction\n\n")
            f.write("*These threads likely contain important PDF attachments*\n\n")
            
            for thread, analysis in list(self.all_evidence['thread_summaries'].items())[:20]:
                # Look for threads likely to have attachments
                if any(word in thread.lower() for word in ['contract', 'legal', 'certificate', 'report', 'list', 'document']):
                    f.write(f"- **{thread}** ({analysis['email_count']} emails)\n")

def main():
    print("Running comprehensive thread analysis...")
    
    # Load emails
    with open('email_catalog/complete_email_catalog.json', 'r') as f:
        emails = json.load(f)
    
    # Parse dates
    for email in emails:
        email['parsed_date'] = datetime.fromisoformat(email['parsed_date'])
    
    # Analyze
    analyzer = ComprehensiveAnalyzer()
    analyzer.extract_all_evidence(emails)
    analyzer.generate_comprehensive_report('comprehensive_analysis')
    
    print(f"\nAnalysis complete!")
    print(f"Total threads analyzed: {len(analyzer.threads_by_subject)}")
    print(f"Jade's emails: {len(analyzer.jade_emails)}")
    print(f"Paul's emails: {len(analyzer.paul_emails)}")
    print(f"Communication issues found: {len(analyzer.all_evidence['communication_issues'])}")
    
    print("\nReports saved to comprehensive_analysis/")

if __name__ == "__main__":
    main()