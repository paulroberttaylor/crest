#!/usr/bin/env python3
"""
Search for specific mortgage impact details
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
    
    print("Searching for specific mortgage impact details...\n")
    
    # Open mbox file
    mbox = mailbox.mbox(mbox_path)
    
    # Key findings
    key_findings = []
    
    # Search for specific amounts and impacts
    for i, message in enumerate(mbox):
        date_str = message.get('Date', '')
        date_obj = parse_date(date_str)
        
        if not date_obj or date_obj.year < 2023:
            continue
        
        subject = decode_header_value(message.get('Subject', ''))
        from_addr = decode_header_value(message.get('From', ''))
        to_addr = decode_header_value(message.get('To', ''))
        body = extract_text_from_message(message)
        
        # Look for specific financial amounts and mortgage discussions
        if any(term in body.lower() for term in ['mortgage', 'rate', 'interest', 'borrowing']):
            # Extract key information
            
            # Check for £6k borrowing drop
            if '£6k' in body or '6k' in body or 'borrowing ability' in body:
                key_findings.append({
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'subject': subject,
                    'from': from_addr,
                    'finding': 'Borrowing ability dropped',
                    'context': extract_context(body, ['£6k', '6k', 'borrowing ability'])
                })
            
            # Check for £7,552.20 extra cost
            if '7,552' in body or '7552' in body:
                key_findings.append({
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'subject': subject,
                    'from': from_addr,
                    'finding': 'Extra mortgage cost: £7,552.20',
                    'context': extract_context(body, ['7,552', '7552'])
                })
            
            # Check for mortgage advisor mentions
            if 'mortgage advisor' in body.lower() and any(term in body.lower() for term in ['rate', 'interest', 'delay']):
                key_findings.append({
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'subject': subject,
                    'from': from_addr,
                    'finding': 'Mortgage advisor rate discussion',
                    'context': extract_context(body, ['mortgage advisor', 'rate', 'interest'])
                })
    
    # Display findings
    print("="*80)
    print("KEY MORTGAGE IMPACT FINDINGS")
    print("="*80)
    
    for finding in sorted(key_findings, key=lambda x: x['date']):
        print(f"\nDate: {finding['date']}")
        print(f"From: {finding['from']}")
        print(f"Subject: {finding['subject']}")
        print(f"Finding: {finding['finding']}")
        print(f"\nContext:")
        print("-"*40)
        print(finding['context'])
    
    # Search for June 2023 emails specifically
    print("\n" + "="*80)
    print("JUNE 2023 DETAILED MORTGAGE DISCUSSIONS")
    print("="*80)
    
    mbox.seek(0)
    june_emails = []
    
    for message in mbox:
        date_obj = parse_date(message.get('Date', ''))
        if date_obj and date_obj.year == 2023 and date_obj.month == 6:
            body = extract_text_from_message(message)
            if 'mortgage' in body.lower() or 'rate' in body.lower() or 'interest' in body.lower():
                june_emails.append({
                    'date': date_obj,
                    'subject': decode_header_value(message.get('Subject', '')),
                    'from': decode_header_value(message.get('From', '')),
                    'body': body
                })
    
    # Show June 8 email with £7,552.20 mention
    for email in sorted(june_emails, key=lambda x: x['date']):
        if '7,552' in email['body'] or 'longer product' in email['body']:
            print(f"\nDate: {email['date'].strftime('%Y-%m-%d %H:%M')}")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print("\nFull relevant section:")
            print("-"*40)
            
            lines = email['body'].split('\n')
            for i, line in enumerate(lines):
                if '7,552' in line or 'longer product' in line:
                    start = max(0, i-3)
                    end = min(len(lines), i+4)
                    for j in range(start, end):
                        print(lines[j])
                    break
    
    mbox.close()

def extract_context(text, search_terms):
    """Extract context around search terms."""
    lines = text.split('\n')
    context_lines = []
    
    for i, line in enumerate(lines):
        for term in search_terms:
            if term.lower() in line.lower():
                start = max(0, i-2)
                end = min(len(lines), i+3)
                context_lines.extend(lines[start:end])
                break
    
    return '\n'.join(list(dict.fromkeys(context_lines)))[:500]

if __name__ == "__main__":
    main()