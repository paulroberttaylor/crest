#!/usr/bin/env python3
"""
Extract specific emails about mortgage expiry threats and NDA
"""

import mailbox
import email
from email.header import decode_header
from datetime import datetime
import json

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

def find_specific_emails():
    """Find specific emails about mortgage threats and NDA."""
    
    # Target dates and subjects
    target_emails = [
        {
            'date': '2023-11-01',
            'subject': '25 Abbots Road - 10 Colt View',
            'from': 'Paul Taylor'
        },
        {
            'date': '2023-11-01', 
            'subject': 'RE: 25 Abbots Road - 10 Colt View',
            'from': 'Hannah Rafferty'
        },
        {
            'date': '2023-11-07',
            'subject': 'RE: 25 Abbots Road - 10 Colt View', 
            'from': 'Hannah Rafferty'
        },
        {
            'date': '2023-12-13',
            'subject': 'RE: [EXTERNAL] URGENT: 10 Colt View',
            'from': 'Hannah Rafferty'
        },
        {
            'date': '2023-12-13',
            'subject': 'Purchase - Plot 34 Albany Wood',
            'from': ['Paul Taylor', 'Hannah Rafferty']
        }
    ]
    
    mbox_files = ["Crest-NHOS-Export.mbox", "Crest-NHOS-Export-001.mbox"]
    found_emails = []
    
    for mbox_file in mbox_files:
        print(f"\nSearching {mbox_file}...")
        
        try:
            mbox = mailbox.mbox(mbox_file)
        except:
            print(f"Could not open {mbox_file}")
            continue
        
        for message in mbox:
            # Get email details
            date_str = message.get('Date', '')
            date_obj = parse_date(date_str)
            
            if not date_obj:
                continue
            
            subject = decode_header_value(message.get('Subject', ''))
            from_addr = decode_header_value(message.get('From', ''))
            to_addr = decode_header_value(message.get('To', ''))
            body = extract_text_from_message(message)
            
            # Check if this matches our targets
            date_match = date_obj.strftime('%Y-%m-%d')
            
            for target in target_emails:
                if target['date'] in date_match:
                    # Check subject match
                    if target['subject'].lower() in subject.lower():
                        # Check from match
                        if isinstance(target['from'], list):
                            from_match = any(f.lower() in from_addr.lower() for f in target['from'])
                        else:
                            from_match = target['from'].lower() in from_addr.lower()
                        
                        if from_match:
                            # Found a match!
                            found_emails.append({
                                'date': date_obj.strftime('%Y-%m-%d %H:%M:%S'),
                                'subject': subject,
                                'from': from_addr,
                                'to': to_addr,
                                'body': body,
                                'key_phrases': extract_key_phrases(body)
                            })
        
        mbox.close()
    
    return found_emails

def extract_key_phrases(body):
    """Extract key phrases about mortgage expiry and NDA."""
    key_phrases = []
    lines = body.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Look for mortgage expiry + NDA mentions
        if ('mortgage' in line_lower and 'expir' in line_lower) or \
           ('non disclosure' in line_lower or 'nda' in line_lower) or \
           ('25 abbots' in line_lower) or \
           ('lose' in line_lower and 'agreement' in line_lower) or \
           ('do the work' in line_lower) or \
           ('best interests' in line_lower):
            
            # Get context (2 lines before and after)
            start = max(0, i-2)
            end = min(len(lines), i+3)
            context = '\n'.join(lines[start:end])
            
            if context.strip():
                key_phrases.append(context.strip())
    
    return key_phrases

def display_results(emails):
    """Display the found emails with key information."""
    
    print("\n" + "="*80)
    print("MORTGAGE EXPIRY THREAT EMAILS - FULL EVIDENCE")
    print("="*80)
    
    # Sort by date
    emails.sort(key=lambda x: x['date'])
    
    for email in emails:
        print(f"\n{'='*80}")
        print(f"Date: {email['date']}")
        print(f"From: {email['from']}")
        print(f"To: {email['to']}")
        print(f"Subject: {email['subject']}")
        print(f"{'-'*80}")
        
        if email['key_phrases']:
            print("\nKEY PHRASES:")
            for phrase in email['key_phrases']:
                print(f"\n{phrase}")
                print("-"*40)
        
        print("\nFULL EMAIL BODY:")
        print(email['body'][:2000])  # First 2000 chars
        if len(email['body']) > 2000:
            print("\n[... email continues ...]")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Found {len(emails)} emails about mortgage expiry threats")
    
    # Extract the key threat
    for email in emails:
        if "if our mortgage offer expires" in email['body'].lower():
            print("\n🚨 KEY THREAT FOUND:")
            for phrase in email['key_phrases']:
                if "mortgage offer expires" in phrase.lower():
                    print(phrase)

def main():
    emails = find_specific_emails()
    display_results(emails)
    
    # Save to JSON
    with open('mortgage_threat_emails.json', 'w') as f:
        json.dump(emails, f, indent=2)
    
    print("\n\nFull email data saved to mortgage_threat_emails.json")

if __name__ == "__main__":
    main()