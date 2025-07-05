#!/usr/bin/env python3
import mailbox
import email
from datetime import datetime
import sys
from email.utils import parsedate_to_datetime, getaddresses
import pytz

def extract_mortgage_emails(mbox_path):
    """Extract all emails from/to mortgage workshop"""
    mbox = mailbox.mbox(mbox_path)
    mortgage_emails = []
    
    for message in mbox:
        try:
            # Get sender
            from_addr = message.get('From', '')
            to_addr = message.get('To', '')
            cc_addr = message.get('Cc', '')
            
            # Check if mortgage workshop is involved
            all_addrs = f"{from_addr} {to_addr} {cc_addr}".lower()
            if 'mortgageworkshop' in all_addrs or 'leanne' in all_addrs:
                # Extract date
                date_str = message.get('Date', '')
                try:
                    date = parsedate_to_datetime(date_str)
                except:
                    date = None
                
                # Get subject
                subject = message.get('Subject', 'No Subject')
                
                # Get body
                body = ""
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                            except:
                                pass
                else:
                    try:
                        body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(message.get_payload())
                
                mortgage_emails.append({
                    'date': date,
                    'from': from_addr,
                    'to': to_addr,
                    'subject': subject,
                    'body': body
                })
        except Exception as e:
            continue
    
    # Sort by date (handle timezone-aware dates)
    def sort_key(x):
        if x['date']:
            return x['date']
        else:
            # Create timezone-aware default date
            return datetime(1970, 1, 1, tzinfo=pytz.UTC)
    
    try:
        mortgage_emails.sort(key=sort_key)
    except:
        # If sort fails, just continue without sorting
        pass
    
    # Print results
    print(f"\nFound {len(mortgage_emails)} emails involving mortgage workshop/Leanne\n")
    
    for email_data in mortgage_emails:
        print("="*80)
        print(f"Date: {email_data['date']}")
        print(f"From: {email_data['from']}")
        print(f"To: {email_data['to']}")
        print(f"Subject: {email_data['subject']}")
        print("\nBody:")
        print(email_data['body'][:1000])  # First 1000 chars
        
        # Look for rate mentions
        body_lower = email_data['body'].lower()
        if '1.5' in body_lower or 'rate' in body_lower or 'percent' in body_lower:
            print("\n*** RATE MENTION FOUND ***")
            # Find context around rate mentions
            for line in email_data['body'].split('\n'):
                if '1.5' in line or 'rate' in line.lower():
                    print(f">>> {line.strip()}")
        print("\n")

if __name__ == "__main__":
    extract_mortgage_emails("Crest-NHOS-Export-001.mbox")