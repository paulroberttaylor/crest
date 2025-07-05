#!/usr/bin/env python3
"""
Find details about the second mortgage offer
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

def find_mortgage_timeline():
    """Find emails about mortgage offers and extensions."""
    
    mbox_files = ["Crest-NHOS-Export.mbox", "Crest-NHOS-Export-001.mbox"]
    
    mortgage_timeline = []
    
    # Keywords to search for
    keywords = [
        'mortgage offer',
        'mortgage expir',
        'mortgage extension',
        'second mortgage',
        'new mortgage',
        'mortgage deadline',
        'mortgage fee',
        'mortgage broker',
        'the mortgage workshop',
        'barclays',
        'mortgage arrangement'
    ]
    
    for mbox_file in mbox_files:
        print(f"\nSearching {mbox_file}...")
        
        try:
            mbox = mailbox.mbox(mbox_file)
        except:
            print(f"Could not open {mbox_file}")
            continue
        
        for message in mbox:
            # Get date
            date_str = message.get('Date', '')
            date_obj = parse_date(date_str)
            
            if not date_obj:
                continue
            
            # Focus on 2023
            if date_obj.year != 2023:
                continue
            
            # Get email details
            subject = decode_header_value(message.get('Subject', ''))
            from_addr = decode_header_value(message.get('From', ''))
            to_addr = decode_header_value(message.get('To', ''))
            body = extract_text_from_message(message)
            
            # Check for mortgage keywords
            body_lower = body.lower()
            subject_lower = subject.lower()
            
            for keyword in keywords:
                if keyword in body_lower or keyword in subject_lower:
                    # Extract relevant context
                    context = extract_mortgage_context(body)
                    
                    if context:
                        mortgage_timeline.append({
                            'date': date_obj,
                            'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                            'subject': subject,
                            'from': from_addr,
                            'to': to_addr,
                            'context': context,
                            'keyword': keyword
                        })
                    break
        
        mbox.close()
    
    return mortgage_timeline

def extract_mortgage_context(body):
    """Extract context about mortgage from email body."""
    lines = body.split('\n')
    context_lines = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Look for mortgage-related lines
        if any(word in line_lower for word in ['mortgage', 'barclays', '£999', '£1495', 'expir', 'deadline', 'offer']):
            # Get surrounding context
            start = max(0, i-2)
            end = min(len(lines), i+3)
            
            for j in range(start, end):
                if lines[j].strip():
                    context_lines.append(lines[j].strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_context = []
    for line in context_lines:
        if line not in seen:
            seen.add(line)
            unique_context.append(line)
    
    return '\n'.join(unique_context[:10])  # Limit to 10 lines

def display_timeline(timeline):
    """Display the mortgage timeline."""
    
    # Sort by date string instead of date object to avoid timezone issues
    timeline.sort(key=lambda x: x['date_str'])
    
    print("\n" + "="*80)
    print("MORTGAGE OFFER TIMELINE - KEY EVENTS")
    print("="*80)
    
    # Group by month
    current_month = None
    
    for event in timeline:
        month = event['date'].strftime('%B %Y')
        
        if month != current_month:
            print(f"\n{'='*40}")
            print(f"{month}")
            print(f"{'='*40}")
            current_month = month
        
        print(f"\n{event['date_str']} - {event['subject'][:60]}")
        print(f"From: {event['from']}")
        print(f"Keyword: {event['keyword']}")
        print(f"\nContext:")
        print(event['context'])
        print("-"*40)
    
    # Find key dates
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    
    # Look for specific patterns
    for event in timeline:
        context_lower = event['context'].lower()
        
        # First mortgage offer
        if 'mortgage offer' in context_lower and event['date'].month <= 6:
            print(f"\n📅 FIRST MORTGAGE OFFER: {event['date_str']}")
            print(f"Context: {event['context'][:200]}")
        
        # Mortgage expiry concerns
        if 'expir' in context_lower:
            print(f"\n⚠️ MORTGAGE EXPIRY CONCERN: {event['date_str']}")
            print(f"Context: {event['context'][:200]}")
        
        # Second mortgage offer
        if ('second' in context_lower or 'new' in context_lower or 'extension' in context_lower) and 'mortgage' in context_lower:
            print(f"\n💰 SECOND MORTGAGE/EXTENSION: {event['date_str']}")
            print(f"Context: {event['context'][:200]}")
        
        # Fees
        if '£999' in event['context'] or '£1495' in event['context']:
            print(f"\n💸 MORTGAGE FEES: {event['date_str']}")
            print(f"Context: {event['context'][:200]}")

def main():
    timeline = find_mortgage_timeline()
    display_timeline(timeline)
    
    print(f"\n\nTotal mortgage-related emails found: {len(timeline)}")

if __name__ == "__main__":
    main()