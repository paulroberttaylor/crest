#!/usr/bin/env python3
"""Comprehensive Leanne and mortgage search report"""

import json
import re
from datetime import datetime
from collections import defaultdict

def comprehensive_search():
    # Load the complete email catalog
    with open('email_catalog/complete_email_catalog.json', 'r') as f:
        emails = json.load(f)
    
    # Results storage
    leanne_details = defaultdict(list)
    mortgage_emails = []
    broker_domains = []
    
    # Common mortgage broker domains
    broker_domain_patterns = [
        r'mortgageworkshop',
        r'themortgageworkshop',
        r'mortgageadvice',
        r'mortgagebroker',
        r'financialadvice',
        r'broker',
        r'lending',
        r'mortgage'
    ]
    
    for email in emails:
        # Get all email text
        from_field = email.get('from', '')
        to_field = email.get('to', '')
        cc_field = email.get('cc', '')
        subject = email.get('subject', '')
        all_text = f"{from_field} {to_field} {cc_field} {subject}"
        
        # Search for Leanne/Leanna with more details
        if re.search(r'leann[ea]?\s', all_text, re.IGNORECASE):
            # Extract details from fields
            if 'leann' in from_field.lower():
                email_match = re.search(r'<([^>]+)>', from_field)
                if email_match:
                    email_addr = email_match.group(1)
                    name = from_field.split('<')[0].strip()
                    
                    leanne_details[email_addr].append({
                        'name': name,
                        'date': email.get('date'),
                        'subject': subject,
                        'to': to_field,
                        'cc': cc_field,
                        'has_attachment': email.get('has_attachment', False),
                        'thread': email.get('thread', ''),
                        'direction': 'FROM Leanne'
                    })
            
            # Also check if Leanne is in TO or CC
            for field, field_name in [(to_field, 'TO'), (cc_field, 'CC')]:
                if 'leann' in field.lower():
                    email_match = re.search(r'leann[ea]?\s[^<]*<([^>]+)>', field, re.IGNORECASE)
                    if email_match:
                        email_addr = email_match.group(1)
                        leanne_details[email_addr].append({
                            'date': email.get('date'),
                            'subject': subject,
                            'from': from_field,
                            'has_attachment': email.get('has_attachment', False),
                            'thread': email.get('thread', ''),
                            'direction': f'{field_name} Leanne'
                        })
        
        # Search for mortgage/broker content
        if re.search(r'mortgage|broker|lending|rate|interest|apr|ltv|arrangement fee', all_text, re.IGNORECASE):
            mortgage_emails.append(email)
        
        # Check for broker domains
        for pattern in broker_domain_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                domains = re.findall(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', all_text)
                for domain in domains:
                    if pattern in domain.lower():
                        broker_domains.append((domain, email))
    
    # Generate report
    print("=== COMPREHENSIVE LEANNE SEARCH RESULTS ===\n")
    
    for email_addr, details in leanne_details.items():
        unique_names = set(d.get('name', '') for d in details if d.get('name'))
        name = list(unique_names)[0] if unique_names else 'Unknown'
        
        print(f"\n{'='*60}")
        print(f"LEANNE: {name}")
        print(f"EMAIL: {email_addr}")
        print(f"TOTAL EMAILS: {len(details)}")
        
        # Group by direction
        from_emails = [d for d in details if d['direction'] == 'FROM Leanne']
        to_emails = [d for d in details if 'TO' in d['direction']]
        cc_emails = [d for d in details if 'CC' in d['direction']]
        
        print(f"\nEmails FROM Leanne: {len(from_emails)}")
        for e in sorted(from_emails, key=lambda x: x['date'])[:5]:
            print(f"  - {e['date']}: {e['subject']}")
            if e['has_attachment']:
                print(f"    ** HAS ATTACHMENT **")
        
        print(f"\nEmails TO Leanne: {len(to_emails)}")
        for e in sorted(to_emails, key=lambda x: x['date'])[:5]:
            print(f"  - {e['date']}: {e['subject']} (from: {e['from']})")
        
        print(f"\nEmails CC Leanne: {len(cc_emails)}")
        print(f"  (First 5 shown)")
    
    print("\n\n=== MORTGAGE-RELATED CONTENT ===")
    print(f"Total emails with mortgage keywords: {len(mortgage_emails)}")
    
    # Group by subject/thread
    mortgage_threads = defaultdict(list)
    for e in mortgage_emails:
        thread = e.get('thread', e.get('subject', 'Unknown'))
        mortgage_threads[thread].append(e)
    
    print("\nMortgage-related threads:")
    for thread, emails_list in sorted(mortgage_threads.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n  Thread: '{thread}' ({len(emails_list)} emails)")
        first_email = sorted(emails_list, key=lambda x: x['date'])[0]
        last_email = sorted(emails_list, key=lambda x: x['date'])[-1]
        print(f"    First: {first_email['date']} - {first_email['subject']}")
        print(f"    Last: {last_email['date']} - {last_email['subject']}")
        
        # Check for attachments
        attachments = [e for e in emails_list if e.get('has_attachment')]
        if attachments:
            print(f"    ** {len(attachments)} emails with attachments **")
    
    print("\n\n=== BROKER DOMAINS FOUND ===")
    unique_domains = set(d[0] for d in broker_domains)
    if unique_domains:
        for domain in unique_domains:
            print(f"  - {domain}")
    else:
        print("  No broker-specific domains found")
    
    # Check specific mortgage fee thread
    print("\n\n=== MORTGAGE BROKER FEE THREAD ANALYSIS ===")
    fee_thread = [e for e in emails if 'Mortgage Broker Fee' in e.get('subject', '')]
    if fee_thread:
        print(f"Found {len(fee_thread)} emails about mortgage broker fees")
        for e in sorted(fee_thread, key=lambda x: x['date']):
            print(f"\n  Date: {e['date']}")
            print(f"  Subject: {e['subject']}")
            print(f"  From: {e['from']}")
            print(f"  To: {e['to']}")
            if e.get('has_attachment'):
                print(f"  ** HAS ATTACHMENT **")

if __name__ == "__main__":
    comprehensive_search()