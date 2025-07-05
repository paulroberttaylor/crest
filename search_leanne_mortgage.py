#!/usr/bin/env python3
"""Search for Leanne emails and mortgage-related content"""

import json
import re
from datetime import datetime
from collections import defaultdict

def search_emails():
    # Load the complete email catalog
    with open('email_catalog/complete_email_catalog.json', 'r') as f:
        emails = json.load(f)
    
    # Results storage
    leanne_emails = defaultdict(list)
    mortgage_emails = []
    mortgage_workshop_emails = []
    
    # Patterns
    leanne_pattern = re.compile(r'leann[ea]?\s', re.IGNORECASE)
    mortgage_pattern = re.compile(r'mortgage|broker|lending|loan|rate|interest\s*rate|apr|ltv', re.IGNORECASE)
    mortgage_workshop_pattern = re.compile(r'mortgage\s*workshop', re.IGNORECASE)
    
    # Search through all emails
    for email in emails:
        # Check all fields for Leanne
        all_text = f"{email.get('from', '')} {email.get('to', '')} {email.get('cc', '')} {email.get('subject', '')}"
        
        if leanne_pattern.search(all_text):
            # Extract Leanne's email address
            from_field = email.get('from', '')
            if 'leann' in from_field.lower():
                # Extract email address
                match = re.search(r'<([^>]+)>', from_field)
                if match:
                    leanne_email = match.group(1)
                    leanne_name = from_field.split('<')[0].strip()
                else:
                    leanne_email = from_field
                    leanne_name = from_field
                
                leanne_emails[leanne_email].append({
                    'date': email.get('date'),
                    'subject': email.get('subject'),
                    'from': from_field,
                    'to': email.get('to'),
                    'has_attachment': email.get('has_attachment', False)
                })
        
        # Check for mortgage content
        if mortgage_pattern.search(all_text):
            mortgage_emails.append(email)
        
        # Check for Mortgage Workshop
        if mortgage_workshop_pattern.search(all_text):
            mortgage_workshop_emails.append(email)
    
    # Print results
    print("=== LEANNE EMAIL SEARCH RESULTS ===\n")
    
    for leanne_email, emails_list in leanne_emails.items():
        print(f"\nLeanne: {leanne_email}")
        print(f"Total emails: {len(emails_list)}")
        print("\nEmails:")
        for e in sorted(emails_list, key=lambda x: x['date']):
            print(f"  Date: {e['date']}")
            print(f"  Subject: {e['subject']}")
            print(f"  Has attachment: {e['has_attachment']}")
            print()
    
    print("\n=== MORTGAGE-RELATED EMAILS ===")
    print(f"Total mortgage-related emails: {len(mortgage_emails)}")
    
    # Show first 10 mortgage emails
    for e in mortgage_emails[:10]:
        print(f"\nDate: {e.get('date')}")
        print(f"Subject: {e.get('subject')}")
        print(f"From: {e.get('from')}")
        print(f"Has attachment: {e.get('has_attachment', False)}")
    
    print(f"\n=== THE MORTGAGE WORKSHOP EMAILS ===")
    print(f"Total: {len(mortgage_workshop_emails)}")
    
    for e in mortgage_workshop_emails:
        print(f"\nDate: {e.get('date')}")
        print(f"Subject: {e.get('subject')}")
        print(f"From: {e.get('from')}")
        print(f"To: {e.get('to')}")

if __name__ == "__main__":
    search_emails()