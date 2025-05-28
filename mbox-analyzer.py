#!/usr/bin/env python3
"""
MBOX Email Analyzer for Crest Nicholson Correspondence
Analyzes emails from/to specified domains and creates organized output
"""

import mailbox
import email
from email.utils import parsedate_to_datetime
from datetime import datetime
import csv
import json
import os
import re
from collections import defaultdict

# Domains to analyze
DOMAINS = [
    'crestnicholson.com',
    'nhos.org.uk'
]

YOUR_EMAIL = 'paulroberttaylor@gmail.com'

def extract_email_addresses(field):
    """Extract email addresses from a field (To, From, CC, etc)"""
    if not field:
        return []
    # Handle both string and Header objects
    field_str = str(field)
    # Find all email addresses
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', field_str.lower())
    return emails

def is_relevant_email(msg):
    """Check if email involves our domains of interest"""
    # Get all email addresses from the message
    from_addresses = extract_email_addresses(msg.get('From', ''))
    to_addresses = extract_email_addresses(msg.get('To', ''))
    cc_addresses = extract_email_addresses(msg.get('CC', ''))
    
    all_addresses = from_addresses + to_addresses + cc_addresses
    
    # Check if any address matches our domains
    for addr in all_addresses:
        for domain in DOMAINS:
            if domain in addr:
                return True
    
    return False

def get_email_body(msg):
    """Extract email body from message"""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body += str(part.get_payload())
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            body = str(msg.get_payload())
    
    return body.strip()

def analyze_mbox(mbox_path, output_dir='email_analysis'):
    """Main analysis function"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Open MBOX file
    mbox = mailbox.mbox(mbox_path)
    
    # Storage for analysis
    emails_by_domain = defaultdict(list)
    all_emails = []
    timeline = []
    
    print(f"Analyzing {len(mbox)} emails...")
    
    for i, msg in enumerate(mbox):
        if i % 1000 == 0:
            print(f"Processing email {i}...")
        
        if not is_relevant_email(msg):
            continue
        
        # Extract email data
        email_data = {
            'subject': msg.get('Subject', 'No Subject'),
            'from': msg.get('From', ''),
            'to': msg.get('To', ''),
            'cc': msg.get('CC', ''),
            'date_str': msg.get('Date', ''),
            'message_id': msg.get('Message-ID', ''),
            'in_reply_to': msg.get('In-Reply-To', ''),
            'body': get_email_body(msg)
        }
        
        # Parse date
        try:
            email_data['date'] = parsedate_to_datetime(email_data['date_str'])
        except:
            email_data['date'] = None
        
        # Categorize by domain
        from_addresses = extract_email_addresses(email_data['from'])
        for addr in from_addresses:
            for domain in DOMAINS:
                if domain in addr:
                    emails_by_domain[domain].append(email_data)
                    break
        
        all_emails.append(email_data)
        
        # Add to timeline if date is valid
        if email_data['date']:
            timeline.append({
                'date': email_data['date'],
                'subject': email_data['subject'],
                'from': email_data['from'],
                'to': email_data['to']
            })
    
    print(f"Found {len(all_emails)} relevant emails")
    
    # Sort timeline
    timeline.sort(key=lambda x: x['date'])
    
    # Write outputs
    
    # 1. CSV summary
    with open(os.path.join(output_dir, 'email_summary.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'subject', 'from', 'to', 'cc'])
        writer.writeheader()
        for email in sorted(all_emails, key=lambda x: x['date'] or datetime.min):
            writer.writerow({
                'date': email['date'].isoformat() if email['date'] else 'Unknown',
                'subject': email['subject'],
                'from': email['from'],
                'to': email['to'],
                'cc': email['cc']
            })
    
    # 2. Timeline markdown
    with open(os.path.join(output_dir, 'timeline.md'), 'w', encoding='utf-8') as f:
        f.write("# Email Timeline\n\n")
        current_month = None
        
        for item in timeline:
            month = item['date'].strftime('%Y-%m')
            if month != current_month:
                f.write(f"\n## {item['date'].strftime('%B %Y')}\n\n")
                current_month = month
            
            f.write(f"**{item['date'].strftime('%Y-%m-%d %H:%M')}**\n")
            f.write(f"- Subject: {item['subject']}\n")
            f.write(f"- From: {item['from']}\n")
            f.write(f"- To: {item['to']}\n\n")
    
    # 3. Domain summaries
    for domain, emails in emails_by_domain.items():
        with open(os.path.join(output_dir, f'{domain.replace(".", "_")}_emails.md'), 'w', encoding='utf-8') as f:
            f.write(f"# Emails from {domain}\n\n")
            f.write(f"Total: {len(emails)} emails\n\n")
            
            for email in sorted(emails, key=lambda x: x['date'] or datetime.min):
                f.write(f"## {email['date'].strftime('%Y-%m-%d %H:%M') if email['date'] else 'Unknown Date'}: {email['subject']}\n")
                f.write(f"**From:** {email['from']}\n")
                f.write(f"**To:** {email['to']}\n")
                if email['cc']:
                    f.write(f"**CC:** {email['cc']}\n")
                f.write(f"\n{email['body'][:500]}...\n")
                f.write("\n---\n\n")
    
    # 4. Statistics
    stats = {
        'total_emails': len(all_emails),
        'by_domain': {domain: len(emails) for domain, emails in emails_by_domain.items()},
        'date_range': {
            'earliest': min(e['date'] for e in all_emails if e['date']).isoformat() if all_emails else None,
            'latest': max(e['date'] for e in all_emails if e['date']).isoformat() if all_emails else None
        }
    }
    
    with open(os.path.join(output_dir, 'statistics.json'), 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\nAnalysis complete! Results saved to {output_dir}/")
    print(f"- email_summary.csv: Spreadsheet of all emails")
    print(f"- timeline.md: Chronological timeline")
    print(f"- *_emails.md: Emails grouped by domain")
    print(f"- statistics.json: Summary statistics")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python mbox-analyzer.py <path_to_mbox_file>")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    
    if not os.path.exists(mbox_path):
        print(f"Error: File {mbox_path} not found")
        sys.exit(1)
    
    analyze_mbox(mbox_path)