#!/usr/bin/env python3
"""
Comprehensive Email Analyzer for NHOS Complaint
Reads EVERY email from Jan 1, 2023 onwards and logs ALL complaints/dissatisfaction
"""

import mailbox
import email
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import json
import csv
import re
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import os

class ComplaintAnalyzer:
    def __init__(self, mbox_path: str):
        self.mbox_path = mbox_path
        self.all_issues = []
        self.issue_categories = defaultdict(list)
        self.timeline = []
        self.people_involved = defaultdict(set)
        
        # Keywords and phrases indicating problems/dissatisfaction
        self.complaint_indicators = {
            'delays': ['delay', 'late', 'overdue', 'behind schedule', 'postponed', 'pushed back', 'still waiting'],
            'quality': ['defect', 'issue', 'problem', 'fault', 'damage', 'broken', 'not working', 'poor quality', 'substandard'],
            'communication': ['no response', 'not heard', 'chasing', 'follow up', 'ignored', 'still awaiting', 'promised but'],
            'promises': ['promised', 'assured', 'told us', 'guaranteed', 'committed', 'agreed to', 'supposed to'],
            'frustration': ['disappointed', 'frustrated', 'unacceptable', 'appalling', 'disgusted', 'angry', 'upset'],
            'escalation': ['complaint', 'escalate', 'formal', 'solicitor', 'legal', 'ombudsman', 'NHBC'],
            'safety': ['dangerous', 'unsafe', 'hazard', 'risk', 'safety concern', 'health and safety'],
            'completion': ['snagging', 'incomplete', 'not finished', 'outstanding', 'still to do', 'not ready'],
            'process': ['misled', 'misinformed', 'incorrect', 'wrong information', 'not told', 'pressure', 'forced'],
            'requests': ['please can', 'could you', 'we need', 'require', 'request', 'asking for', 'want to know']
        }
        
        # Specific known issues to track
        self.specific_issues = [
            'air brick', 'render', 'path', 'driveway', 'garden', 'fence', 'boundary',
            'completion', 'handover', 'exchange', 'mortgage', 'warranty', 'certificate',
            'drainage', 'water', 'leak', 'damp', 'crack', 'paint', 'plaster',
            'kitchen', 'bathroom', 'bedroom', 'window', 'door', 'floor', 'ceiling',
            'heating', 'boiler', 'electrical', 'plumbing', 'insulation',
            'parking', 'access', 'neighbour', 'noise', 'dust', 'mess'
        ]
        
        # Track email metadata
        self.email_threads = defaultdict(list)
        self.response_times = []
        
    def parse_email_date(self, msg) -> datetime:
        """Extract date from email message."""
        date_str = msg.get('Date', '')
        try:
            parsed_date = parsedate_to_datetime(date_str)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except:
            return datetime.now(timezone.utc)
    
    def extract_email_content(self, msg) -> str:
        """Extract all text content from email."""
        content = []
        
        # Add subject
        subject = msg.get('Subject', '')
        content.append(f"Subject: {subject}")
        
        # Extract body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        content.append(body)
                    except:
                        pass
                elif part.get_content_type() == 'text/html':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Simple HTML stripping
                        body = re.sub('<[^<]+?>', '', body)
                        content.append(body)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                content.append(body)
            except:
                pass
        
        return '\n'.join(content).lower()
    
    def analyze_email_for_issues(self, msg, content: str, date: datetime) -> List[Dict]:
        """Analyze email content for any signs of complaints or dissatisfaction."""
        issues_found = []
        
        # Check for complaint indicators
        for category, keywords in self.complaint_indicators.items():
            for keyword in keywords:
                if keyword in content:
                    # Extract context around keyword
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if keyword in line:
                            context_start = max(0, i-2)
                            context_end = min(len(lines), i+3)
                            context = '\n'.join(lines[context_start:context_end])
                            
                            issue = {
                                'date': date.isoformat(),
                                'category': category,
                                'keyword': keyword,
                                'subject': msg.get('Subject', ''),
                                'from': msg.get('From', ''),
                                'to': msg.get('To', ''),
                                'context': context.strip(),
                                'thread_id': msg.get('Message-ID', ''),
                                'in_reply_to': msg.get('In-Reply-To', '')
                            }
                            issues_found.append(issue)
        
        # Check for specific issues
        for specific_issue in self.specific_issues:
            if specific_issue in content:
                # Find sentences containing the issue
                sentences = re.split(r'[.!?]', content)
                for sentence in sentences:
                    if specific_issue in sentence and len(sentence.strip()) > 10:
                        issue = {
                            'date': date.isoformat(),
                            'category': 'specific_issue',
                            'keyword': specific_issue,
                            'subject': msg.get('Subject', ''),
                            'from': msg.get('From', ''),
                            'to': msg.get('To', ''),
                            'context': sentence.strip(),
                            'thread_id': msg.get('Message-ID', ''),
                            'in_reply_to': msg.get('In-Reply-To', '')
                        }
                        issues_found.append(issue)
        
        # Check if this is Paul or Jade complaining/asking for something
        from_addr = msg.get('From', '').lower()
        if 'paulroberttaylor@gmail.com' in from_addr or 'jade.millington@hotmail.co.uk' in from_addr:
            # Look for question marks - often indicate requests or concerns
            if '?' in content:
                questions = [s.strip() for s in content.split('?') if len(s.strip()) > 10]
                for question in questions[:3]:  # Limit to first 3 questions
                    issue = {
                        'date': date.isoformat(),
                        'category': 'question/concern',
                        'keyword': '?',
                        'subject': msg.get('Subject', ''),
                        'from': msg.get('From', ''),
                        'to': msg.get('To', ''),
                        'context': question + '?',
                        'thread_id': msg.get('Message-ID', ''),
                        'in_reply_to': msg.get('In-Reply-To', '')
                    }
                    issues_found.append(issue)
        
        return issues_found
    
    def analyze_response_patterns(self):
        """Analyze email threads for response time issues."""
        for thread_id, emails in self.email_threads.items():
            if len(emails) < 2:
                continue
                
            # Sort by date
            emails.sort(key=lambda x: x['date'])
            
            for i in range(1, len(emails)):
                prev_email = emails[i-1]
                curr_email = emails[i]
                
                # Check if this is Paul/Jade waiting for response
                if ('paulroberttaylor@gmail.com' in prev_email['from'].lower() or 
                    'jade.millington@hotmail.co.uk' in prev_email['from'].lower()):
                    
                    # Calculate response time
                    time_diff = curr_email['date'] - prev_email['date']
                    days_waiting = time_diff.days
                    
                    if days_waiting > 3:  # More than 3 days for response
                        issue = {
                            'date': prev_email['date'].isoformat(),
                            'category': 'slow_response',
                            'keyword': f'{days_waiting} days waiting',
                            'subject': prev_email['subject'],
                            'from': prev_email['from'],
                            'to': prev_email['to'],
                            'context': f"Waited {days_waiting} days for response to: {prev_email['subject']}",
                            'thread_id': thread_id,
                            'in_reply_to': ''
                        }
                        self.all_issues.append(issue)
    
    def process_mbox(self):
        """Process all emails from Jan 1, 2023 onwards."""
        print("Opening mbox file...")
        mbox = mailbox.mbox(self.mbox_path)
        
        cutoff_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        total_emails = 0
        processed_emails = 0
        
        print("Processing emails...")
        for msg in mbox:
            total_emails += 1
            
            # Get email date
            email_date = self.parse_email_date(msg)
            
            # Skip emails before Jan 1, 2023
            if email_date < cutoff_date:
                continue
            
            processed_emails += 1
            
            # Extract content
            content = self.extract_email_content(msg)
            
            # Analyze for issues
            issues = self.analyze_email_for_issues(msg, content, email_date)
            self.all_issues.extend(issues)
            
            # Track for thread analysis
            thread_id = msg.get('In-Reply-To', msg.get('Message-ID', ''))
            self.email_threads[thread_id].append({
                'date': email_date,
                'from': msg.get('From', ''),
                'to': msg.get('To', ''),
                'subject': msg.get('Subject', ''),
                'message_id': msg.get('Message-ID', '')
            })
            
            # Track people involved
            from_addr = msg.get('From', '')
            if from_addr:
                self.people_involved[email_date.strftime('%Y-%m')].add(from_addr)
            
            if processed_emails % 100 == 0:
                print(f"Processed {processed_emails} emails from Jan 2023 onwards...")
        
        print(f"\nTotal emails in mbox: {total_emails}")
        print(f"Emails from Jan 2023 onwards: {processed_emails}")
        print(f"Issues/complaints found: {len(self.all_issues)}")
        
        # Analyze response patterns
        print("\nAnalyzing response patterns...")
        self.analyze_response_patterns()
        
        # Organize by category
        for issue in self.all_issues:
            self.issue_categories[issue['category']].append(issue)
    
    def generate_report(self):
        """Generate comprehensive report of all issues."""
        os.makedirs('complaint_analysis', exist_ok=True)
        
        # 1. Detailed CSV of all issues
        print("\nGenerating detailed CSV...")
        with open('complaint_analysis/all_issues_detailed.csv', 'w', newline='', encoding='utf-8') as f:
            if self.all_issues:
                fieldnames = self.all_issues[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for issue in sorted(self.all_issues, key=lambda x: x['date']):
                    writer.writerow(issue)
        
        # 2. Summary by category
        print("Generating category summary...")
        with open('complaint_analysis/issue_categories.md', 'w', encoding='utf-8') as f:
            f.write("# Issues by Category\n\n")
            
            for category, issues in sorted(self.issue_categories.items()):
                f.write(f"## {category.replace('_', ' ').title()} ({len(issues)} issues)\n\n")
                
                # Group by month
                by_month = defaultdict(list)
                for issue in issues:
                    month = issue['date'][:7]  # YYYY-MM
                    by_month[month].append(issue)
                
                for month in sorted(by_month.keys()):
                    f.write(f"### {month}\n")
                    for issue in by_month[month]:
                        f.write(f"- **{issue['date'][:10]}** - {issue['subject']}\n")
                        f.write(f"  - Context: {issue['context'][:200]}...\n")
                f.write("\n")
        
        # 3. Chronological timeline
        print("Generating timeline...")
        with open('complaint_analysis/chronological_timeline.md', 'w', encoding='utf-8') as f:
            f.write("# Complete Chronological Timeline of Issues\n\n")
            
            # Group by date
            by_date = defaultdict(list)
            for issue in self.all_issues:
                date = issue['date'][:10]
                by_date[date].append(issue)
            
            for date in sorted(by_date.keys()):
                f.write(f"## {date}\n")
                for issue in by_date[date]:
                    f.write(f"- **{issue['category']}**: {issue['subject']}\n")
                    f.write(f"  - {issue['context'][:300]}...\n")
                f.write("\n")
        
        # 4. Key findings summary
        print("Generating summary...")
        with open('complaint_analysis/key_findings.md', 'w', encoding='utf-8') as f:
            f.write("# Key Findings Summary\n\n")
            f.write(f"- **Total issues found**: {len(self.all_issues)}\n")
            f.write(f"- **Date range**: Jan 1, 2023 to present\n\n")
            
            f.write("## Issues by Category:\n")
            for category, issues in sorted(self.issue_categories.items(), key=lambda x: -len(x[1])):
                f.write(f"- {category.replace('_', ' ').title()}: {len(issues)}\n")
            
            f.write("\n## Most Frequent Keywords:\n")
            keyword_counts = defaultdict(int)
            for issue in self.all_issues:
                keyword_counts[issue['keyword']] += 1
            
            for keyword, count in sorted(keyword_counts.items(), key=lambda x: -x[1])[:20]:
                f.write(f"- '{keyword}': {count} times\n")
            
            f.write("\n## People Most Involved:\n")
            people_counts = defaultdict(int)
            for issue in self.all_issues:
                people_counts[issue['from']] += 1
                people_counts[issue['to']] += 1
            
            for person, count in sorted(people_counts.items(), key=lambda x: -x[1])[:10]:
                if '@' in person:
                    f.write(f"- {person}: {count} issue-related emails\n")
        
        # 5. Evidence strength analysis
        print("Analyzing evidence strength...")
        with open('complaint_analysis/evidence_strength.json', 'w') as f:
            evidence = {
                'total_issues': len(self.all_issues),
                'categories': {cat: len(issues) for cat, issues in self.issue_categories.items()},
                'date_range': {
                    'start': min(issue['date'] for issue in self.all_issues) if self.all_issues else None,
                    'end': max(issue['date'] for issue in self.all_issues) if self.all_issues else None
                },
                'unique_threads': len(set(issue['thread_id'] for issue in self.all_issues if issue['thread_id'])),
                'slow_responses': len([i for i in self.all_issues if i['category'] == 'slow_response'])
            }
            json.dump(evidence, f, indent=2)
        
        print("\nAnalysis complete! Check the 'complaint_analysis' directory for results.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python comprehensive-complaint-analyzer.py <mbox_file>")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    
    if not os.path.exists(mbox_path):
        print(f"Error: File '{mbox_path}' not found")
        sys.exit(1)
    
    analyzer = ComplaintAnalyzer(mbox_path)
    analyzer.process_mbox()
    analyzer.generate_report()

if __name__ == "__main__":
    main()