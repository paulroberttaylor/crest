#!/usr/bin/env python3
"""
Search for Plot 34 contract delay emails
"""

import mailbox
import email
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import re
import sys

def parse_email_date(msg):
    """Extract date from email message."""
    date_str = msg.get('Date', '')
    try:
        parsed_date = parsedate_to_datetime(date_str)
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        return parsed_date
    except:
        return None

def extract_email_content(msg):
    """Extract all text content from email."""
    content = []
    
    # Add subject
    subject = msg.get('Subject', '')
    content.append(f"Subject: {subject}")
    
    # Extract body
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    content.append(body)
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            content.append(body)
        except:
            pass
    
    return '\n'.join(content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python search-plot34-contract-delays.py <mbox_file>")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    
    print("Searching for Plot 34 contract delays...\n")
    
    mbox = mailbox.mbox(mbox_path)
    
    # Keywords to search for
    plot_keywords = ['plot 34', '10 colt view', 'albany wood']
    delay_keywords = ['delay', 'late', 'wait', 'chase', 'urgent', 'asap', 'still', 'when will', 'when can']
    contract_keywords = ['contract', 'exchange', 'completion', 'complete']
    
    found_emails = []
    
    for msg in mbox:
        content = extract_email_content(msg).lower()
        
        # Check if this email mentions plot 34
        has_plot = any(keyword in content for keyword in plot_keywords)
        if not has_plot:
            continue
        
        # Check if it mentions contracts/exchange/completion
        has_contract = any(keyword in content for keyword in contract_keywords)
        if not has_contract:
            continue
        
        # Check if it mentions delays or urgency
        has_delay = any(keyword in content for keyword in delay_keywords)
        
        # Also look for specific phrases
        delay_phrases = [
            'not ready',
            'not able to',
            'cannot exchange',
            'cannot complete',
            'need more time',
            'pushed back',
            'revised date',
            'new date',
            'update on',
            'still waiting',
            'any update',
            'chasing',
            'following up'
        ]
        
        has_delay_phrase = any(phrase in content for phrase in delay_phrases)
        
        if has_delay or has_delay_phrase:
            date = parse_email_date(msg)
            if date and date.year >= 2023:
                # Extract relevant context
                lines = content.split('\n')
                relevant_lines = []
                
                for i, line in enumerate(lines):
                    if any(kw in line for kw in contract_keywords + delay_keywords + delay_phrases):
                        # Get context around the line
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        relevant_lines.extend(lines[start:end])
                
                found_emails.append({
                    'date': date,
                    'subject': msg.get('Subject', ''),
                    'from': msg.get('From', ''),
                    'to': msg.get('To', ''),
                    'context': '\n'.join(set(relevant_lines))[:500]
                })
    
    # Sort by date
    found_emails.sort(key=lambda x: x['date'])
    
    print(f"Found {len(found_emails)} emails about Plot 34 contract delays:\n")
    
    for email_data in found_emails:
        print(f"Date: {email_data['date'].strftime('%Y-%m-%d')}")
        print(f"Subject: {email_data['subject']}")
        print(f"From: {email_data['from']}")
        print(f"To: {email_data['to']}")
        print(f"Context:\n{email_data['context']}")
        print("-" * 80)

if __name__ == "__main__":
    main()