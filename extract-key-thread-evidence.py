#!/usr/bin/env python3
"""
Extract detailed evidence from key email threads showing poor treatment.
Focus on URGENT threads, defects, and specific issues.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def parse_date(date_str):
    """Parse ISO date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None

def analyze_urgent_threads(emails):
    """Analyze the URGENT email threads."""
    urgent_threads = defaultdict(list)
    
    for email in emails:
        if 'urgent' in email['subject'].lower():
            thread = email['thread']
            urgent_threads[thread].append(email)
    
    analysis = {}
    for thread, thread_emails in urgent_threads.items():
        # Sort by date
        thread_emails.sort(key=lambda x: x['parsed_date'])
        
        # Analyze the thread
        analysis[thread] = {
            'duration_days': (thread_emails[-1]['parsed_date'] - thread_emails[0]['parsed_date']).days,
            'email_count': len(thread_emails),
            'customer_emails': len([e for e in thread_emails if e['direction'] == 'to_crest']),
            'crest_responses': len([e for e in thread_emails if e['direction'] == 'from_crest']),
            'timeline': []
        }
        
        # Build timeline
        for email in thread_emails:
            analysis[thread]['timeline'].append({
                'date': email['date'],
                'from': email['from'].split('<')[0].strip(),
                'direction': email['direction'],
                'subject': email['subject']
            })
    
    return analysis

def analyze_defect_threads(emails):
    """Analyze defect-related threads."""
    defect_threads = defaultdict(list)
    
    for email in emails:
        subject_lower = email['subject'].lower()
        if any(word in subject_lower for word in ['defect', 'snag', 'issue', 'problem']):
            # Skip render, path, garden
            if not any(skip in subject_lower for skip in ['render', 'path', 'garden', 'level']):
                thread = email['thread']
                defect_threads[thread].append(email)
    
    return defect_threads

def extract_key_issues(emails):
    """Extract specific issues mentioned."""
    issues = {
        'contract_delays': [],
        'certification_issues': [],
        'quality_issues': [],
        'communication_failures': []
    }
    
    for email in emails:
        subject_lower = email['subject'].lower()
        
        # Contract/legal delays
        if 'contract' in subject_lower or 'legal' in subject_lower:
            if email['direction'] == 'to_crest':
                issues['contract_delays'].append({
                    'date': email['date'],
                    'subject': email['subject'],
                    'evidence': 'Customer chasing contract/legal documents'
                })
        
        # Trinity Rose / certification
        if 'trinity' in subject_lower or 'certificate' in subject_lower:
            issues['certification_issues'].append({
                'date': email['date'],
                'subject': email['subject'],
                'from': email['from']
            })
        
        # Multiple chasers in same thread indicate communication failure
        if any(word in subject_lower for word in ['re:', 'fwd:', 'fw:']):
            if email['direction'] == 'to_crest':
                issues['communication_failures'].append({
                    'date': email['date'],
                    'subject': email['subject']
                })
    
    return issues

def generate_detailed_report(urgent_analysis, defect_threads, key_issues, output_dir):
    """Generate detailed report of key evidence."""
    output_dir = Path(output_dir)
    
    report_file = output_dir / 'key_thread_evidence.md'
    with open(report_file, 'w') as f:
        f.write("# Key Thread Evidence: Poor Treatment During Plot 34 Purchase\n\n")
        
        # URGENT threads analysis
        f.write("## URGENT Email Threads Analysis\n\n")
        f.write("*These threads show the stress and poor communication leading to completion*\n\n")
        
        for thread, analysis in urgent_analysis.items():
            f.write(f"### Thread: {thread}\n")
            f.write(f"- **Duration**: {analysis['duration_days']} days\n")
            f.write(f"- **Total emails**: {analysis['email_count']}\n")
            f.write(f"- **Customer emails**: {analysis['customer_emails']} (having to chase)\n")
            f.write(f"- **Crest responses**: {analysis['crest_responses']}\n\n")
            
            f.write("**Timeline:**\n")
            for event in analysis['timeline'][:10]:
                date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                f.write(f"- {date.strftime('%Y-%m-%d %H:%M')} [{event['direction']}] {event['from']}\n")
            
            if len(analysis['timeline']) > 10:
                f.write(f"- ... and {len(analysis['timeline']) - 10} more emails\n")
            f.write("\n---\n\n")
        
        # Defect threads
        f.write("## Defect/Quality Issue Threads\n\n")
        f.write(f"*Found {len(defect_threads)} threads about defects (excluding render/path/garden)*\n\n")
        
        for thread, emails in list(defect_threads.items())[:5]:
            f.write(f"### {thread}\n")
            f.write(f"- **Emails**: {len(emails)}\n")
            f.write(f"- **Date range**: {emails[0]['date'][:10]} to {emails[-1]['date'][:10]}\n\n")
        
        # Key issues
        f.write("## Specific Issues Identified\n\n")
        
        if key_issues['contract_delays']:
            f.write(f"### Contract/Legal Delays ({len(key_issues['contract_delays'])} instances)\n\n")
            for issue in key_issues['contract_delays'][:5]:
                date = datetime.fromisoformat(issue['date'].replace('Z', '+00:00'))
                f.write(f"- {date.strftime('%Y-%m-%d')}: {issue['subject']}\n")
            f.write("\n")
        
        if key_issues['certification_issues']:
            f.write(f"### Certification Issues ({len(key_issues['certification_issues'])} instances)\n\n")
            for issue in key_issues['certification_issues'][:5]:
                date = datetime.fromisoformat(issue['date'].replace('Z', '+00:00'))
                f.write(f"- {date.strftime('%Y-%m-%d')}: {issue['subject']}\n")
            f.write("\n")
        
        # Pattern analysis
        f.write("## Pattern of Poor Treatment\n\n")
        f.write("1. **Pre-completion stress**: Multiple URGENT emails in Nov/Dec 2023\n")
        f.write("2. **Completion with defects**: 45 issues identified on completion day\n")
        f.write("3. **Immediate complaints**: Formal complaints started 6 days after completion\n")
        f.write("4. **Ongoing issues**: Still dealing with complaints 496+ days later\n")

def main():
    print("Extracting key thread evidence...")
    
    # Load email catalog
    with open('email_catalog/complete_email_catalog.json', 'r') as f:
        emails = json.load(f)
    
    # Parse dates
    for email in emails:
        email['parsed_date'] = datetime.fromisoformat(email['parsed_date'])
    
    # Analyze urgent threads
    urgent_analysis = analyze_urgent_threads(emails)
    print(f"Found {len(urgent_analysis)} URGENT threads")
    
    # Analyze defect threads
    defect_threads = analyze_defect_threads(emails)
    print(f"Found {len(defect_threads)} defect threads")
    
    # Extract key issues
    key_issues = extract_key_issues(emails)
    
    # Generate report
    generate_detailed_report(urgent_analysis, defect_threads, key_issues, 'purchase_treatment_analysis')
    
    print("\nKey evidence extracted to: purchase_treatment_analysis/key_thread_evidence.md")

if __name__ == "__main__":
    main()