#!/usr/bin/env python3
"""
Search MBOX file for mortgage-related information
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
        # Try parsing with parsedate_to_datetime
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except:
        return None

def main():
    mbox_path = "Crest-NHOS-Export.mbox"
    
    print(f"Searching {mbox_path} for mortgage-related information...")
    print("Focus: 1.5% rate, mortgage impacts from delays\n")
    
    # Open mbox file
    mbox = mailbox.mbox(mbox_path)
    
    mortgage_emails = []
    rate_mentions = []
    june_july_2023 = []
    mortgage_impact_emails = []
    
    # Search patterns
    mortgage_patterns = [
        r'mortgage', r'broker', r'advisor', r'lending', r'lender',
        r'interest rate', r'completion delay', r'financial impact'
    ]
    
    rate_pattern = r'1\.5\s*%|1\.5\s*percent|one point five'
    
    for i, message in enumerate(mbox):
        # Get date
        date_str = message.get('Date', '')
        date_obj = parse_date(date_str)
        
        if not date_obj:
            continue
            
        # Only process emails from 2023 onwards
        if date_obj.year < 2023:
            continue
        
        # Get headers
        subject = decode_header_value(message.get('Subject', ''))
        from_addr = decode_header_value(message.get('From', ''))
        to_addr = decode_header_value(message.get('To', ''))
        
        # Get body
        body = extract_text_from_message(message)
        full_content = f"{subject}\n{body}".lower()
        
        # Check for mortgage-related content
        is_mortgage_related = any(re.search(pattern, full_content, re.IGNORECASE) for pattern in mortgage_patterns)
        
        if is_mortgage_related:
            email_data = {
                'date': date_obj,
                'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'body': body[:1000]  # First 1000 chars
            }
            
            mortgage_emails.append(email_data)
            
            # Check for rate mentions
            if re.search(rate_pattern, body, re.IGNORECASE):
                rate_mentions.append(email_data)
            
            # Check if June-July 2023
            if date_obj.year == 2023 and date_obj.month in [6, 7]:
                june_july_2023.append(email_data)
            
            # Check for delay impact discussions
            if 'delay' in full_content and ('mortgage' in full_content or 'rate' in full_content):
                mortgage_impact_emails.append(email_data)
    
    print(f"Found {len(mortgage_emails)} mortgage-related emails\n")
    
    # Display rate mentions
    print("="*80)
    print("EMAILS MENTIONING 1.5% RATE")
    print("="*80)
    
    if rate_mentions:
        for email in rate_mentions:
            print(f"\nDate: {email['date_str']}")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print("\nContent excerpt:")
            print("-"*40)
            
            # Find and highlight rate mention
            lines = email['body'].split('\n')
            for line in lines:
                if re.search(rate_pattern, line, re.IGNORECASE):
                    print(f">>> {line.strip()}")
                    # Show context
                    idx = lines.index(line)
                    if idx > 0:
                        print(f"    {lines[idx-1].strip()}")
                    if idx < len(lines) - 1:
                        print(f"    {lines[idx+1].strip()}")
                    break
    else:
        print("\nNo direct mentions of 1.5% rate found")
    
    # Display June-July 2023 mortgage discussions
    print("\n" + "="*80)
    print("JUNE-JULY 2023 MORTGAGE DISCUSSIONS")
    print("="*80)
    
    for email in sorted(june_july_2023, key=lambda x: x['date'])[:10]:
        print(f"\nDate: {email['date_str']}")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        
        # Extract key sentences
        sentences = email['body'].split('.')
        relevant_sentences = []
        for sent in sentences:
            sent_lower = sent.lower()
            if any(term in sent_lower for term in ['mortgage', 'rate', 'delay', 'completion', 'interest']):
                relevant_sentences.append(sent.strip())
        
        if relevant_sentences:
            print("\nKey content:")
            for sent in relevant_sentences[:3]:
                if sent:
                    print(f"  - {sent}")
    
    # Display delay impact emails
    print("\n" + "="*80)
    print("EMAILS DISCUSSING MORTGAGE IMPACT FROM DELAYS")
    print("="*80)
    
    for email in sorted(mortgage_impact_emails, key=lambda x: x['date'])[:10]:
        print(f"\nDate: {email['date_str']}")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        
        # Find delay + mortgage mentions
        lines = email['body'].split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if 'delay' in line_lower and any(term in line_lower for term in ['mortgage', 'rate', 'interest']):
                print(f"\nRelevant excerpt:")
                print("-"*40)
                start = max(0, i-1)
                end = min(len(lines), i+2)
                for j in range(start, end):
                    print(lines[j].strip())
                break
    
    # Search for specific mortgage amounts mentioned
    print("\n" + "="*80)
    print("MORTGAGE FEES AND ARRANGEMENTS")
    print("="*80)
    
    fee_pattern = r'£\d{3,4}|mortgage.*fee|broker.*fee|arrangement.*fee'
    
    for email in mortgage_emails:
        if re.search(fee_pattern, email['body'], re.IGNORECASE):
            print(f"\nDate: {email['date_str']}")
            print(f"Subject: {email['subject']}")
            
            # Find fee mentions
            lines = email['body'].split('\n')
            for line in lines:
                if re.search(fee_pattern, line, re.IGNORECASE):
                    print(f"  Fee mention: {line.strip()}")
    
    mbox.close()

if __name__ == "__main__":
    main()