#!/usr/bin/env python3
"""
Search for mortgage timeline information, focusing on expiry and extensions
"""

import mailbox
import email
from email.header import decode_header
from datetime import datetime
import re

def decode_header_value(header):
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
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except:
        return None

# Search for specific mortgage timeline info
mbox = mailbox.mbox("Crest-NHOS-Export.mbox")

# Focus on emails from key periods
timeline_emails = []
mortgage_mentions = []

print("Searching for mortgage timeline information...")
print("="*80)

for message in mbox:
    date_obj = parse_date(message.get('Date', ''))
    if not date_obj or date_obj.year < 2023:
        continue
    
    subject = decode_header_value(message.get('Subject', ''))
    from_addr = decode_header_value(message.get('From', ''))
    to_addr = decode_header_value(message.get('To', ''))
    body = extract_text_from_message(message)
    
    # Look for specific mortgage patterns
    body_lower = body.lower()
    
    # Check for mortgage offer validity/expiry
    if any(pattern in body_lower for pattern in [
        'mortgage offer valid',
        'mortgage offer expir',
        'mortgage expires',
        'mortgage expired',
        'offer expires',
        'offer valid',
        '6 months',
        'six months',
        'mortgage extension',
        'extend mortgage',
        'mortgage deadline',
        'mortgage rescind'
    ]):
        # Extract relevant lines
        lines = body.split('\n')
        relevant_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(term in line_lower for term in [
                'mortgage', 'offer', 'expir', 'valid', 'extend',
                '6 month', 'six month', 'rescind', 'deadline'
            ]):
                # Get context
                start = max(0, i-2)
                end = min(len(lines), i+3)
                context = '\n'.join(lines[start:end])
                relevant_lines.append(context)
        
        if relevant_lines:
            mortgage_mentions.append({
                'date': date_obj,
                'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'relevant_content': relevant_lines
            })

# Sort by date
mortgage_mentions.sort(key=lambda x: x['date'])

# Display findings chronologically
print("\nMORTGAGE OFFER TIMELINE - KEY MENTIONS")
print("="*80)

# First, look for mortgage offer dates
print("\n1. MORTGAGE OFFER VALIDITY/EXPIRY MENTIONS:")
print("-"*80)

for email in mortgage_mentions:
    # Check if this email mentions specific dates or timeframes
    has_timeline_info = False
    for content in email['relevant_content']:
        if any(term in content.lower() for term in ['valid', 'expir', '6 month', 'six month', 'extend']):
            has_timeline_info = True
            break
    
    if has_timeline_info:
        print(f"\nDate: {email['date_str']}")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print("\nRelevant content:")
        
        for content in email['relevant_content'][:2]:  # Show first 2 relevant excerpts
            print("-"*40)
            print(content)

# Now search for completion delays and their impact
print("\n\n2. COMPLETION DELAYS AFFECTING MORTGAGE:")
print("="*80)

delay_emails = []

# Re-scan for delay impacts
mbox = mailbox.mbox("Crest-NHOS-Export.mbox")

for message in mbox:
    date_obj = parse_date(message.get('Date', ''))
    if not date_obj or date_obj.year < 2023:
        continue
    
    # Focus on key months: June-December 2023
    if not (date_obj.year == 2023 and 6 <= date_obj.month <= 12):
        continue
    
    subject = decode_header_value(message.get('Subject', ''))
    from_addr = decode_header_value(message.get('From', ''))
    body = extract_text_from_message(message)
    
    # Look for delay + mortgage mentions
    if 'delay' in body.lower() and 'mortgage' in body.lower():
        lines = body.split('\n')
        for i, line in enumerate(lines):
            if 'delay' in line.lower() and ('mortgage' in line.lower() or 
                                            'completion' in line.lower() or
                                            'exchange' in line.lower()):
                context_start = max(0, i-3)
                context_end = min(len(lines), i+4)
                context = '\n'.join(lines[context_start:context_end])
                
                delay_emails.append({
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'subject': subject,
                    'from': from_addr,
                    'context': context
                })
                break

# Display delay impacts
for email in sorted(delay_emails, key=lambda x: x['date'])[:10]:
    print(f"\nDate: {email['date']}")
    print(f"From: {email['from']}")
    print(f"Subject: {email['subject']}")
    print("\nContext:")
    print("-"*40)
    print(email['context'])

mbox.close()

print("\n\nSUMMARY:")
print("="*80)
print(f"Found {len(mortgage_mentions)} emails mentioning mortgage offer validity/expiry")
print(f"Found {len(delay_emails)} emails linking delays to mortgage issues")