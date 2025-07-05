#!/usr/bin/env python3
"""
Find the specific June 8, 2023 email with £7,552.20 mention
"""

import mailbox
import email
from email.header import decode_header
from datetime import datetime
import re

def decode_header_value(header):
    """Decode email header value."""
    if not header:
        return ""
    decoded_parts = decode_header(header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                result.append(str(part, errors='ignore'))
        else:
            result.append(str(part))
    return ' '.join(result)

def extract_text_from_message(msg):
    """Extract text content from email message."""
    text_parts = []
    
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    text_parts.append(text)
                except:
                    pass
    else:
        try:
            text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            text_parts.append(text)
        except:
            pass
    
    return '\n'.join(text_parts)

def parse_date(date_str):
    """Parse email date string to datetime object."""
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except:
        return None

def main():
    mbox_path = "Crest-NHOS-Export.mbox"
    
    print("Searching for June 2023 emails with specific mortgage impact information...\n")
    
    # Open mbox file
    mbox = mailbox.mbox(mbox_path)
    
    june_2023_emails = []
    
    for message in mbox:
        date_obj = parse_date(message.get('Date', ''))
        
        if date_obj and date_obj.year == 2023 and date_obj.month in [6, 7]:
            subject = decode_header_value(message.get('Subject', ''))
            from_addr = decode_header_value(message.get('From', ''))
            to_addr = decode_header_value(message.get('To', ''))
            body = extract_text_from_message(message)
            
            # Look for emails mentioning mortgage costs or specific amounts
            if any(term in body for term in ['7,552', '7552', 'mortgage advisor', '£6k', 'borrowing ability', 'interest rate']):
                june_2023_emails.append({
                    'date': date_obj,
                    'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': subject,
                    'from': from_addr,
                    'to': to_addr,
                    'body': body
                })
    
    # Sort by date
    june_2023_emails.sort(key=lambda x: x['date'])
    
    print("="*80)
    print("KEY MORTGAGE IMPACT EMAILS FROM JUNE-JULY 2023")
    print("="*80)
    
    for email in june_2023_emails:
        # Check for specific mentions
        if '7,552' in email['body'] or '7552' in email['body']:
            print(f"\n[FOUND: £7,552.20 EXTRA MORTGAGE COST]")
            print(f"Date: {email['date_str']}")
            print(f"From: {email['from']}")
            print(f"To: {email['to']}")
            print(f"Subject: {email['subject']}")
            print("\nFull context:")
            print("-"*40)
            
            # Find and show the specific paragraph
            lines = email['body'].split('\n')
            for i, line in enumerate(lines):
                if '7,552' in line or '7552' in line:
                    start = max(0, i-5)
                    end = min(len(lines), i+5)
                    for j in range(start, end):
                        if j == i:
                            print(f">>> {lines[j]}")
                        else:
                            print(f"    {lines[j]}")
            print("="*80)
        
        elif '£6k' in email['body'] or 'borrowing ability' in email['body']:
            print(f"\n[FOUND: BORROWING ABILITY DROPPED]")
            print(f"Date: {email['date_str']}")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print("\nRelevant excerpt:")
            print("-"*40)
            
            lines = email['body'].split('\n')
            for i, line in enumerate(lines):
                if '£6k' in line or 'borrowing ability' in line:
                    start = max(0, i-3)
                    end = min(len(lines), i+3)
                    for j in range(start, end):
                        print(lines[j])
                    break
            print("="*80)
    
    # Look for mortgage principle mentions
    print("\n" + "="*80)
    print("MORTGAGE IN PRINCIPLE / RATE DISCUSSIONS")
    print("="*80)
    
    for email in june_2023_emails:
        if 'mortgage' in email['body'].lower() and ('principle' in email['body'].lower() or 'rate' in email['body'].lower()):
            print(f"\nDate: {email['date_str']}")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            
            # Extract key sentences
            sentences = email['body'].split('.')
            relevant = []
            for sent in sentences:
                if any(term in sent.lower() for term in ['mortgage', 'rate', 'interest', 'delay', 'expire']):
                    relevant.append(sent.strip())
            
            if relevant:
                print("\nKey points:")
                for r in relevant[:5]:
                    if r:
                        print(f"  • {r}")
    
    mbox.close()

if __name__ == "__main__":
    main()