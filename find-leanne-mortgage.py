#!/usr/bin/env python3
"""
Search for emails from/to Leanne/Leanna about mortgage rates
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
    
    print("Searching for emails from/to Leanne/Leanna about mortgage rates...")
    print("="*80)
    
    # Open mbox file
    mbox = mailbox.mbox(mbox_path)
    
    leanne_emails = []
    
    # Search patterns
    leanne_pattern = r'leann[ae]'
    mortgage_keywords = ['mortgage', 'rate', 'interest', '1.5', 'percent', 'broker', 'lending', 'offer', 'product']
    
    for i, message in enumerate(mbox):
        # Get headers
        subject = decode_header_value(message.get('Subject', ''))
        from_addr = decode_header_value(message.get('From', ''))
        to_addr = decode_header_value(message.get('To', ''))
        cc_addr = decode_header_value(message.get('Cc', ''))
        
        # Check if Leanne is involved
        all_headers = f"{from_addr} {to_addr} {cc_addr}".lower()
        
        if re.search(leanne_pattern, all_headers, re.IGNORECASE):
            # Get date
            date_str = message.get('Date', '')
            date_obj = parse_date(date_str)
            
            if not date_obj:
                continue
            
            # Get body
            body = extract_text_from_message(message)
            full_content = f"{subject}\n{body}".lower()
            
            # Check for mortgage-related content
            has_mortgage_content = any(keyword in full_content for keyword in mortgage_keywords)
            
            if has_mortgage_content or '1.5' in body:
                email_data = {
                    'date': date_obj,
                    'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': subject,
                    'from': from_addr,
                    'to': to_addr,
                    'cc': cc_addr,
                    'body': body,
                    'leanne_sender': bool(re.search(leanne_pattern, from_addr, re.IGNORECASE))
                }
                leanne_emails.append(email_data)
    
    # Sort by date string to avoid timezone issues
    leanne_emails.sort(key=lambda x: x['date_str'])
    
    print(f"\nFound {len(leanne_emails)} emails involving Leanne with mortgage content\n")
    
    # Display all emails
    for email_data in leanne_emails:
        print("="*80)
        print(f"Date: {email_data['date_str']}")
        print(f"From: {email_data['from']}")
        print(f"To: {email_data['to']}")
        if email_data['cc']:
            print(f"CC: {email_data['cc']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Leanne is sender: {'Yes' if email_data['leanne_sender'] else 'No'}")
        print("\nFull email content:")
        print("-"*40)
        
        # Print full body
        print(email_data['body'][:3000])  # First 3000 chars
        
        if len(email_data['body']) > 3000:
            print("\n[... email continues ...]")
        
        print("\n")
        
        # Look for specific rate mentions
        if '1.5' in email_data['body']:
            print("*** FOUND 1.5 MENTION ***")
            lines = email_data['body'].split('\n')
            for i, line in enumerate(lines):
                if '1.5' in line:
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    print("\nContext around 1.5 mention:")
                    for j in range(start, end):
                        if j == i:
                            print(f">>> {lines[j]}")
                        else:
                            print(f"    {lines[j]}")
        
        print("\n")
    
    # Also search for any email mentioning both mortgage and specific rates
    print("\n" + "="*80)
    print("SEARCHING ALL EMAILS FOR RATE MENTIONS (not just Leanne)")
    print("="*80)
    
    mbox = mailbox.mbox(mbox_path)  # Reopen
    rate_emails = []
    
    for message in mbox:
        body = extract_text_from_message(message)
        
        # Look for specific rate patterns
        rate_patterns = [
            r'1\.5\s*%',
            r'1\.5\s*percent',
            r'one point five',
            r'mortgage.*rate.*\d+\.?\d*\s*%',
            r'rate.*mortgage.*\d+\.?\d*\s*%',
            r'interest rate.*\d+\.?\d*\s*%'
        ]
        
        for pattern in rate_patterns:
            if re.search(pattern, body, re.IGNORECASE):
                date_obj = parse_date(message.get('Date', ''))
                if date_obj and date_obj.year >= 2023:
                    rate_emails.append({
                        'date': date_obj.strftime('%Y-%m-%d'),
                        'from': decode_header_value(message.get('From', '')),
                        'subject': decode_header_value(message.get('Subject', '')),
                        'body_excerpt': body[:500],
                        'pattern': pattern
                    })
                    break
    
    if rate_emails:
        print(f"\nFound {len(rate_emails)} emails with specific rate mentions:")
        for email in sorted(rate_emails, key=lambda x: x['date']):
            print(f"\n{email['date']} - {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Pattern matched: {email['pattern']}")
    
    mbox.close()

if __name__ == "__main__":
    main()