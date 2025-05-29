#!/usr/bin/env python3
"""
Distinct Issues Analyzer - Identifies unique issues without duplication
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
import hashlib
import os

class DistinctIssueAnalyzer:
    def __init__(self, mbox_path: str):
        self.mbox_path = mbox_path
        self.distinct_issues = {}  # Key: issue hash, Value: issue details
        self.issue_threads = defaultdict(set)  # Track which threads discuss each issue
        self.email_cache = {}  # Cache processed emails to detect replies/forwards
        
        # Define specific issues to track
        self.tracked_issues = {
            'air_brick': {
                'patterns': ['air brick', 'airbrick', 'ventilation brick', 'buried brick'],
                'first_mention': None,
                'description': 'Air brick buried under driveway'
            },
            'render_crack': {
                'patterns': ['render crack', 'crack in render', 'render issue', 'rendering crack'],
                'first_mention': None,
                'description': 'Cracks in external render'
            },
            'path_levels': {
                'patterns': ['path level', 'pathway', 'access path', 'bridal path', 'bridle path'],
                'first_mention': None,
                'description': 'Path levels and access issues'
            },
            'garden_levels': {
                'patterns': ['garden level', 'garden slope', 'garden gradient', 'rear garden'],
                'first_mention': None,
                'description': 'Garden levels not as expected'
            },
            'completion_delays': {
                'patterns': ['completion delay', 'delayed completion', 'completion date', 'pushed back'],
                'first_mention': None,
                'description': 'Delays to completion date'
            },
            'snagging_items': {
                'patterns': ['snag', 'snagging', 'defect', 'incomplete work'],
                'first_mention': None,
                'description': 'Snagging items at completion'
            },
            'communication_failures': {
                'patterns': ['no response', 'not heard back', 'chasing', 'still waiting', 'ignored'],
                'first_mention': None,
                'description': 'Failures to respond to communications'
            },
            'broken_promises': {
                'patterns': ['promised but', 'told us', 'assured us', 'commitment not', 'failed to'],
                'first_mention': None,
                'description': 'Broken promises and commitments'
            },
            'fence_issues': {
                'patterns': ['fence', 'fencing', 'boundary fence'],
                'first_mention': None,
                'description': 'Issues with fencing/boundaries'
            },
            'drainage': {
                'patterns': ['drainage', 'water pooling', 'standing water', 'drain'],
                'first_mention': None,
                'description': 'Drainage and water issues'
            },
            'driveway': {
                'patterns': ['driveway', 'drive issues', 'tarmac'],
                'first_mention': None,
                'description': 'Driveway problems'
            },
            'warranty_issues': {
                'patterns': ['warranty', 'NHBC', 'warranty claim'],
                'first_mention': None,
                'description': 'Warranty and NHBC issues'
            },
            'legal_threats': {
                'patterns': ['solicitor', 'legal action', 'legal advice', 'lawyer'],
                'first_mention': None,
                'description': 'Legal action threatened or taken'
            },
            'complaint_escalation': {
                'patterns': ['formal complaint', 'ombudsman', 'escalate', 'NHOS'],
                'first_mention': None,
                'description': 'Formal complaints and escalations'
            },
            'exchange_issues': {
                'patterns': ['exchange delay', 'exchange date', 'exchange problem'],
                'first_mention': None,
                'description': 'Problems with exchange process'
            },
            'mortgage_issues': {
                'patterns': ['mortgage delay', 'mortgage problem', 'mortgage offer'],
                'first_mention': None,
                'description': 'Mortgage-related delays'
            },
            'buyback_problems': {
                'patterns': ['buy back', 'buyback', '25 abbots', 'abbots road'],
                'first_mention': None,
                'description': 'Issues with 25 Abbots Road buyback'
            },
            'pressure_tactics': {
                'patterns': ['pressur', 'forced', 'threat', 'ultimatum'],
                'first_mention': None,
                'description': 'Pressure tactics used'
            },
            'misinformation': {
                'patterns': ['incorrect information', 'wrong information', 'misled', 'misinformed'],
                'first_mention': None,
                'description': 'Provided incorrect information'
            },
            'safety_concerns': {
                'patterns': ['unsafe', 'dangerous', 'safety', 'hazard'],
                'first_mention': None,
                'description': 'Safety concerns raised'
            }
        }
        
        # Track complaint patterns
        self.complaint_timeline = []
        self.response_delays = []
        
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
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                content.append(body)
            except:
                pass
        
        return '\n'.join(content).lower()
    
    def is_duplicate_content(self, content: str, msg_id: str) -> bool:
        """Check if this is duplicate content (forward/reply of same issue)."""
        # Create content hash (first 500 chars after removing common reply prefixes)
        cleaned = re.sub(r'^(re:|fwd:|fw:)\s*', '', content.strip()[:500])
        content_hash = hashlib.md5(cleaned.encode()).hexdigest()
        
        if content_hash in self.email_cache:
            return True
        
        self.email_cache[content_hash] = msg_id
        return False
    
    def extract_distinct_issues(self, msg, content: str, date: datetime):
        """Extract distinct issues from email content."""
        from_addr = msg.get('From', '').lower()
        to_addr = msg.get('To', '').lower()
        subject = msg.get('Subject', '')
        msg_id = msg.get('Message-ID', '')
        
        # Skip if this looks like duplicate content
        if self.is_duplicate_content(content, msg_id):
            return
        
        # Check for tracked issues
        for issue_key, issue_data in self.tracked_issues.items():
            for pattern in issue_data['patterns']:
                if pattern in content:
                    # Check if this is the first mention or a new context
                    if issue_data['first_mention'] is None:
                        issue_data['first_mention'] = {
                            'date': date,
                            'subject': subject,
                            'from': from_addr,
                            'to': to_addr,
                            'context': self.extract_context(content, pattern)
                        }
                        
                        # Add to distinct issues
                        issue_id = f"{issue_key}_{date.strftime('%Y%m%d')}"
                        self.distinct_issues[issue_id] = {
                            'type': issue_key,
                            'description': issue_data['description'],
                            'first_mentioned': date.isoformat(),
                            'subject': subject,
                            'from': from_addr,
                            'to': to_addr,
                            'context': issue_data['first_mention']['context']
                        }
                    
                    # Track which threads discuss this issue
                    thread_id = msg.get('In-Reply-To', msg_id)
                    self.issue_threads[issue_key].add(thread_id)
                    break
        
        # Look for complaints from Paul/Jade that don't fit tracked categories
        if 'paulroberttaylor@gmail.com' in from_addr or 'jade.millington@hotmail.co.uk' in from_addr:
            # Look for complaint language
            complaint_phrases = [
                'this is unacceptable',
                'we are disappointed',
                'this is not what we',
                'you promised',
                'we were told',
                'still waiting',
                'please can you',
                'urgent',
                'asap',
                'immediately'
            ]
            
            for phrase in complaint_phrases:
                if phrase in content:
                    issue_hash = hashlib.md5(f"{date}_{phrase}_{subject}".encode()).hexdigest()[:8]
                    if issue_hash not in self.distinct_issues:
                        self.distinct_issues[issue_hash] = {
                            'type': 'general_complaint',
                            'description': f'Complaint: {phrase}',
                            'first_mentioned': date.isoformat(),
                            'subject': subject,
                            'from': from_addr,
                            'to': to_addr,
                            'context': self.extract_context(content, phrase)
                        }
                    break
    
    def extract_context(self, content: str, keyword: str, context_size: int = 200) -> str:
        """Extract context around keyword."""
        lower_content = content.lower()
        pos = lower_content.find(keyword.lower())
        if pos == -1:
            return ""
        
        start = max(0, pos - context_size)
        end = min(len(content), pos + len(keyword) + context_size)
        
        context = content[start:end].strip()
        
        # Clean up context
        context = re.sub(r'\s+', ' ', context)
        context = re.sub(r'[>\n\r\t]', ' ', context)
        
        return context
    
    def analyze_response_patterns(self):
        """Analyze email threads for response delays."""
        threads = defaultdict(list)
        
        # Re-open mbox for second pass
        mbox = mailbox.mbox(self.mbox_path)
        for msg in mbox:
            thread_id = msg.get('In-Reply-To', msg.get('Message-ID', ''))
            date = self.parse_email_date(msg)
            from_addr = msg.get('From', '').lower()
            
            threads[thread_id].append({
                'date': date,
                'from': from_addr,
                'subject': msg.get('Subject', '')
            })
        
        # Analyze threads for delays
        for thread_emails in threads.values():
            if len(thread_emails) < 2:
                continue
            
            # Sort by date
            thread_emails.sort(key=lambda x: x['date'])
            
            for i in range(1, len(thread_emails)):
                prev = thread_emails[i-1]
                curr = thread_emails[i]
                
                # Check if Paul/Jade sent email and waited for response
                if ('paulroberttaylor@gmail.com' in prev['from'] or 
                    'jade.millington@hotmail.co.uk' in prev['from']):
                    
                    days_waited = (curr['date'] - prev['date']).days
                    
                    if days_waited > 7:  # More than a week
                        delay_id = f"delay_{prev['date'].strftime('%Y%m%d')}_{days_waited}d"
                        if delay_id not in self.distinct_issues:
                            self.distinct_issues[delay_id] = {
                                'type': 'response_delay',
                                'description': f'Waited {days_waited} days for response',
                                'first_mentioned': prev['date'].isoformat(),
                                'subject': prev['subject'],
                                'from': prev['from'],
                                'to': 'Crest Nicholson',
                                'context': f"Email sent {prev['date'].strftime('%Y-%m-%d')}, response received {curr['date'].strftime('%Y-%m-%d')}"
                            }
    
    def process_mbox(self):
        """Process all emails from Jan 1, 2023 onwards."""
        print("Opening mbox file...")
        mbox = mailbox.mbox(self.mbox_path)
        
        cutoff_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        total_emails = 0
        processed_emails = 0
        
        print("Processing emails for distinct issues...")
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
            
            # Extract distinct issues
            self.extract_distinct_issues(msg, content, email_date)
            
            if processed_emails % 100 == 0:
                print(f"Processed {processed_emails} emails...")
        
        print(f"\nTotal emails in mbox: {total_emails}")
        print(f"Emails from Jan 2023 onwards: {processed_emails}")
        
        # Analyze response patterns
        print("\nAnalyzing response patterns...")
        self.analyze_response_patterns()
        
        print(f"Distinct issues found: {len(self.distinct_issues)}")
    
    def generate_report(self):
        """Generate report of distinct issues."""
        os.makedirs('distinct_issues_analysis', exist_ok=True)
        
        # 1. Summary report
        print("\nGenerating summary report...")
        with open('distinct_issues_analysis/distinct_issues_summary.md', 'w', encoding='utf-8') as f:
            f.write("# Distinct Issues Summary\n\n")
            f.write(f"**Total distinct issues identified**: {len(self.distinct_issues)}\n\n")
            
            # Count by type
            issue_types = defaultdict(int)
            for issue in self.distinct_issues.values():
                issue_types[issue['type']] += 1
            
            f.write("## Issues by Type:\n")
            for issue_type, count in sorted(issue_types.items(), key=lambda x: -x[1]):
                # Get description from tracked issues
                desc = ""
                for key, data in self.tracked_issues.items():
                    if key == issue_type:
                        desc = data['description']
                        break
                if not desc:
                    desc = issue_type.replace('_', ' ').title()
                
                f.write(f"- **{desc}**: {count} instances\n")
            
            f.write("\n## Chronological Timeline of Distinct Issues:\n\n")
            
            # Sort by date
            sorted_issues = sorted(self.distinct_issues.items(), 
                                 key=lambda x: x[1]['first_mentioned'])
            
            current_month = None
            for issue_id, issue in sorted_issues:
                issue_date = datetime.fromisoformat(issue['first_mentioned'])
                month = issue_date.strftime('%B %Y')
                
                if month != current_month:
                    f.write(f"\n### {month}\n\n")
                    current_month = month
                
                f.write(f"**{issue_date.strftime('%Y-%m-%d')}** - {issue['description']}\n")
                f.write(f"- Subject: {issue['subject']}\n")
                f.write(f"- Context: {issue['context'][:200]}...\n\n")
        
        # 2. Detailed CSV
        print("Generating detailed CSV...")
        with open('distinct_issues_analysis/distinct_issues_detailed.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['date', 'type', 'description', 'subject', 'from', 'to', 'context']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for issue in sorted(self.distinct_issues.values(), key=lambda x: x['first_mentioned']):
                writer.writerow({
                    'date': issue['first_mentioned'][:10],
                    'type': issue['type'],
                    'description': issue['description'],
                    'subject': issue['subject'],
                    'from': issue['from'],
                    'to': issue['to'],
                    'context': issue['context']
                })
        
        # 3. Key findings
        print("Generating key findings...")
        with open('distinct_issues_analysis/key_findings.md', 'w', encoding='utf-8') as f:
            f.write("# Key Findings - Distinct Issues Only\n\n")
            
            # First mentions of major issues
            f.write("## First Occurrence of Major Issues:\n\n")
            for key, data in self.tracked_issues.items():
                if data['first_mention']:
                    fm = data['first_mention']
                    f.write(f"**{data['description']}**: {fm['date'].strftime('%Y-%m-%d')}\n")
                    f.write(f"- Subject: {fm['subject']}\n")
                    f.write(f"- Context: {fm['context'][:150]}...\n\n")
            
            # Response delay analysis
            delays = [i for i in self.distinct_issues.values() if i['type'] == 'response_delay']
            if delays:
                f.write(f"\n## Response Delays: {len(delays)} instances\n")
                f.write("Occasions where you waited over a week for responses:\n\n")
                for delay in sorted(delays, key=lambda x: x['first_mentioned']):
                    f.write(f"- {delay['first_mentioned'][:10]}: {delay['description']}\n")
        
        # 4. Evidence strength
        print("Generating evidence analysis...")
        with open('distinct_issues_analysis/evidence_strength.json', 'w') as f:
            evidence = {
                'total_distinct_issues': len(self.distinct_issues),
                'issue_types': dict(issue_types),
                'tracked_issues_found': sum(1 for i in self.tracked_issues.values() if i['first_mention']),
                'response_delays': len(delays),
                'date_range': {
                    'start': min(i['first_mentioned'] for i in self.distinct_issues.values()) if self.distinct_issues else None,
                    'end': max(i['first_mentioned'] for i in self.distinct_issues.values()) if self.distinct_issues else None
                }
            }
            json.dump(evidence, f, indent=2)
        
        print("\nAnalysis complete! Check 'distinct_issues_analysis' directory.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python distinct-issues-analyzer.py <mbox_file>")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    
    if not os.path.exists(mbox_path):
        print(f"Error: File '{mbox_path}' not found")
        sys.exit(1)
    
    analyzer = DistinctIssueAnalyzer(mbox_path)
    analyzer.process_mbox()
    analyzer.generate_report()

if __name__ == "__main__":
    main()