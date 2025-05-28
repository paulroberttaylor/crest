#!/usr/bin/env python3
"""
Extract evidence of poor treatment during Plot 34 purchase and early ownership.
Focus on broken promises, delays, poor workmanship, having to chase, etc.
Excludes render and path issues (covered in existing complaints).
"""

import json
from datetime import datetime
from pathlib import Path
import re

class PurchaseTreatmentAnalyzer:
    def __init__(self):
        self.evidence = {
            'broken_promises': [],
            'delays': [],
            'poor_workmanship': [],
            'having_to_chase': [],
            'documentation_issues': [],
            'dismissive_responses': [],
            'timeline_violations': []
        }
        self.key_events = []
        
    def parse_date(self, date_str):
        """Parse ISO date string to datetime object."""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def analyze_for_evidence(self, email):
        """Analyze email for evidence of poor treatment."""
        subject_lower = email['subject'].lower()
        
        # Skip render and path issues (existing complaints)
        if any(word in subject_lower for word in ['render', 'path', 'cycle', 'bridal', 'bridleway', 'access']):
            return
            
        # Skip garden levels (settled)
        if 'garden' in subject_lower and 'level' in subject_lower:
            return
            
        # Look for broken promises/delays
        if any(word in subject_lower for word in ['contract', 'legal', 'document']):
            if any(word in subject_lower for word in ['chase', 'await', 'urgent', 'reminder']):
                self.evidence['broken_promises'].append({
                    'date': email['date'],
                    'subject': email['subject'],
                    'evidence': 'Had to chase for contract/legal documents',
                    'thread': email['thread']
                })
                
        # Documentation issues
        if any(word in subject_lower for word in ['nhbc', 'certificate', 'warranty']):
            self.evidence['documentation_issues'].append({
                'date': email['date'],
                'subject': email['subject'],
                'evidence': 'Issues with documentation/certification',
                'thread': email['thread']
            })
            
        # Having to chase
        if any(word in subject_lower for word in ['urgent', 'chase', 'reminder', 'await', 'follow up', 'following up']):
            self.evidence['having_to_chase'].append({
                'date': email['date'],
                'subject': email['subject'],
                'from': email['from'],
                'to': email['to'],
                'evidence': 'Customer had to chase for response',
                'thread': email['thread']
            })
            
        # Poor workmanship/defects (excluding render)
        if any(word in subject_lower for word in ['defect', 'snag', 'issue', 'problem', 'fault']):
            if 'air brick' in subject_lower or 'airbrick' in subject_lower:
                self.evidence['poor_workmanship'].append({
                    'date': email['date'],
                    'subject': email['subject'],
                    'evidence': 'Air brick issue - buried/blocked',
                    'thread': email['thread']
                })
            elif any(word in subject_lower for word in ['window', 'door', 'kitchen', 'bathroom']):
                self.evidence['poor_workmanship'].append({
                    'date': email['date'],
                    'subject': email['subject'],
                    'evidence': 'Defect in construction/fitting',
                    'thread': email['thread']
                })
                
        # Timeline violations
        if 'completion' in subject_lower or 'complete' in subject_lower:
            self.evidence['timeline_violations'].append({
                'date': email['date'],
                'subject': email['subject'],
                'evidence': 'Completion process issue',
                'thread': email['thread']
            })
            
        # Look for specific issues in complaint documents
        if 'complaint' in subject_lower and email['direction'] == 'from_crest':
            if any(word in subject_lower for word in ['assessment', 'pathway', 'response']):
                self.evidence['dismissive_responses'].append({
                    'date': email['date'],
                    'subject': email['subject'],
                    'from': email['from'],
                    'evidence': 'Complaint response from Crest',
                    'thread': email['thread']
                })
    
    def analyze_timeline_gaps(self, emails):
        """Look for significant gaps in responses."""
        threads = {}
        
        # Group by thread
        for email in emails:
            thread = email['thread']
            if thread not in threads:
                threads[thread] = []
            threads[thread].append(email)
        
        # Analyze each thread for gaps
        for thread, thread_emails in threads.items():
            # Skip if not relevant
            if any(word in thread.lower() for word in ['render', 'path', 'garden level']):
                continue
                
            # Sort by date
            thread_emails.sort(key=lambda x: x['parsed_date'])
            
            # Look for gaps in responses
            for i in range(len(thread_emails) - 1):
                email1 = thread_emails[i]
                email2 = thread_emails[i + 1]
                
                # If customer email followed by Crest response
                if email1['direction'] == 'to_crest' and email2['direction'] == 'from_crest':
                    gap_days = (email2['parsed_date'] - email1['parsed_date']).days
                    
                    if gap_days > 5:  # More than 5 days
                        self.evidence['delays'].append({
                            'date': email1['date'],
                            'subject': email1['subject'],
                            'evidence': f'Crest took {gap_days} days to respond',
                            'thread': thread,
                            'response_date': email2['date']
                        })
    
    def build_timeline(self, emails):
        """Build timeline of key events."""
        events = []
        
        for email in emails:
            subject_lower = email['subject'].lower()
            
            # Key milestones
            if 'reservation' in subject_lower and 'plot 34' in subject_lower:
                events.append({
                    'date': email['date'],
                    'event': 'Property reservation',
                    'subject': email['subject']
                })
            elif 'contract' in subject_lower and any(word in subject_lower for word in ['legal', 'exchange']):
                events.append({
                    'date': email['date'],
                    'event': 'Contract/legal document',
                    'subject': email['subject']
                })
            elif 'completion' in subject_lower and 'letter' in subject_lower:
                events.append({
                    'date': email['date'],
                    'event': 'Completion',
                    'subject': email['subject']
                })
            elif 'snag' in subject_lower or 'defect' in subject_lower:
                if not any(word in subject_lower for word in ['render', 'path', 'garden']):
                    events.append({
                        'date': email['date'],
                        'event': 'Defect/snag reported',
                        'subject': email['subject']
                    })
                    
        self.key_events = sorted(events, key=lambda x: x['date'])
    
    def generate_report(self, output_dir):
        """Generate detailed report of evidence."""
        output_dir = Path(output_dir)
        
        # Save raw evidence
        evidence_file = output_dir / 'purchase_treatment_evidence.json'
        with open(evidence_file, 'w') as f:
            json.dump(self.evidence, f, indent=2)
        
        # Generate markdown report
        report_file = output_dir / 'purchase_treatment_report.md'
        with open(report_file, 'w') as f:
            f.write("# Evidence of Poor Treatment During Plot 34 Purchase\n\n")
            f.write("*This report excludes render and path issues (covered in existing NHOS complaints)*\n\n")
            
            # Timeline
            f.write("## Key Timeline\n\n")
            for event in self.key_events:
                date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                f.write(f"- **{date.strftime('%Y-%m-%d')}**: {event['event']}\n")
                f.write(f"  - {event['subject']}\n\n")
            
            # Evidence categories
            f.write("## Evidence by Category\n\n")
            
            # Broken promises
            if self.evidence['broken_promises']:
                f.write(f"### Broken Promises ({len(self.evidence['broken_promises'])} instances)\n\n")
                for item in self.evidence['broken_promises'][:5]:
                    date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    f.write(f"- **{date.strftime('%Y-%m-%d')}**: {item['subject']}\n")
                    f.write(f"  - Evidence: {item['evidence']}\n\n")
                if len(self.evidence['broken_promises']) > 5:
                    f.write(f"*... and {len(self.evidence['broken_promises']) - 5} more instances*\n\n")
            
            # Delays
            if self.evidence['delays']:
                f.write(f"### Response Delays ({len(self.evidence['delays'])} instances)\n\n")
                for item in self.evidence['delays'][:5]:
                    date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    f.write(f"- **{date.strftime('%Y-%m-%d')}**: {item['subject']}\n")
                    f.write(f"  - {item['evidence']}\n\n")
                if len(self.evidence['delays']) > 5:
                    f.write(f"*... and {len(self.evidence['delays']) - 5} more instances*\n\n")
            
            # Having to chase
            if self.evidence['having_to_chase']:
                f.write(f"### Having to Chase Responses ({len(self.evidence['having_to_chase'])} instances)\n\n")
                for item in self.evidence['having_to_chase'][:10]:
                    date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    f.write(f"- **{date.strftime('%Y-%m-%d')}**: {item['subject']}\n")
                if len(self.evidence['having_to_chase']) > 10:
                    f.write(f"*... and {len(self.evidence['having_to_chase']) - 10} more instances*\n\n")
            
            # Poor workmanship
            if self.evidence['poor_workmanship']:
                f.write(f"### Poor Workmanship/Defects ({len(self.evidence['poor_workmanship'])} instances)\n\n")
                f.write("*Issues you had to identify and point out*\n\n")
                for item in self.evidence['poor_workmanship']:
                    date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    f.write(f"- **{date.strftime('%Y-%m-%d')}**: {item['subject']}\n")
                    f.write(f"  - {item['evidence']}\n\n")
            
            # Documentation issues
            if self.evidence['documentation_issues']:
                f.write(f"### Documentation Issues ({len(self.evidence['documentation_issues'])} instances)\n\n")
                for item in self.evidence['documentation_issues']:
                    date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    f.write(f"- **{date.strftime('%Y-%m-%d')}**: {item['subject']}\n")
                    f.write(f"  - {item['evidence']}\n\n")
            
            # Summary
            f.write("\n## Summary of Evidence\n\n")
            total_evidence = sum(len(items) for items in self.evidence.values())
            f.write(f"- Total pieces of evidence: **{total_evidence}**\n")
            f.write(f"- Instances of having to chase: **{len(self.evidence['having_to_chase'])}**\n")
            f.write(f"- Response delays documented: **{len(self.evidence['delays'])}**\n")
            f.write(f"- Poor workmanship issues: **{len(self.evidence['poor_workmanship'])}**\n")
            f.write(f"- Documentation problems: **{len(self.evidence['documentation_issues'])}**\n")
            
            f.write("\n## Potential NHOS Code Violations\n\n")
            f.write("Based on this evidence, potential violations include:\n\n")
            f.write("- **Part 1.6**: Customer service standards and training\n")
            f.write("- **Part 2.8**: Failure to keep customer informed\n")
            f.write("- **Part 3.1**: After-sales service failures\n")
            f.write("- **Part 3.3**: Defects and snagging issues\n")
            f.write("- **Principle 5**: Lack of responsiveness\n")
            f.write("- **Principle 3**: Quality issues\n")

def main():
    print("Analyzing emails for purchase treatment evidence...")
    
    # Load the email catalog
    with open('email_catalog/complete_email_catalog.json', 'r') as f:
        emails = json.load(f)
    
    # Parse dates
    for email in emails:
        email['parsed_date'] = datetime.fromisoformat(email['parsed_date'])
    
    # Initialize analyzer
    analyzer = PurchaseTreatmentAnalyzer()
    
    # Analyze each email
    for email in emails:
        analyzer.analyze_for_evidence(email)
    
    # Analyze timeline gaps
    analyzer.analyze_timeline_gaps(emails)
    
    # Build timeline
    analyzer.build_timeline(emails)
    
    # Generate report
    analyzer.generate_report('purchase_treatment_analysis')
    
    # Print summary
    print("\n=== Analysis Complete ===")
    print(f"Broken promises: {len(analyzer.evidence['broken_promises'])}")
    print(f"Response delays: {len(analyzer.evidence['delays'])}")
    print(f"Having to chase: {len(analyzer.evidence['having_to_chase'])}")
    print(f"Poor workmanship: {len(analyzer.evidence['poor_workmanship'])}")
    print(f"Documentation issues: {len(analyzer.evidence['documentation_issues'])}")
    print(f"Dismissive responses: {len(analyzer.evidence['dismissive_responses'])}")
    
    print("\nKey files created:")
    print("- purchase_treatment_analysis/purchase_treatment_report.md")
    print("- purchase_treatment_analysis/purchase_treatment_evidence.json")

if __name__ == "__main__":
    main()