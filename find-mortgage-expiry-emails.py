#!/usr/bin/env python3
"""
Find specific emails about mortgage expiry and completion crisis
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

def find_mortgage_crisis_emails():
    """Search for specific mortgage expiry and completion crisis emails."""
    
    mbox_files = ["Crest-NHOS-Export.mbox", "Crest-NHOS-Export-001.mbox"]
    
    key_findings = {
        'mortgage_expiry_threats': [],
        'second_mortgage_offer': [],
        'mortgage_fees': [],
        'urgent_completion': [],
        'jade_emails': []
    }
    
    for mbox_file in mbox_files:
        print(f"\nSearching {mbox_file}...")
        
        try:
            mbox = mailbox.mbox(mbox_file)
        except:
            print(f"Could not open {mbox_file}")
            continue
        
        count = 0
        
        for message in mbox:
            count += 1
            if count % 500 == 0:
                print(f"  Processed {count} emails...")
            
            # Get date
            date_str = message.get('Date', '')
            date_obj = parse_date(date_str)
            
            if not date_obj:
                continue
            
            # Focus on Sept 2023 - Jan 2024
            if not ((date_obj.year == 2023 and date_obj.month >= 9) or 
                    (date_obj.year == 2024 and date_obj.month == 1)):
                continue
            
            # Get email details
            subject = decode_header_value(message.get('Subject', ''))
            from_addr = decode_header_value(message.get('From', ''))
            to_addr = decode_header_value(message.get('To', ''))
            body = extract_text_from_message(message)
            
            # Check for Jade's emails
            if 'jade.millington@hotmail.co.uk' in from_addr.lower() or 'jade' in from_addr.lower():
                if any(word in body.lower() for word in ['mortgage', 'completion', 'urgent', 'delay']):
                    key_findings['jade_emails'].append({
                        'date': date_obj.strftime('%Y-%m-%d %H:%M'),
                        'subject': subject,
                        'from': from_addr,
                        'excerpt': body[:500]
                    })
            
            # Search for mortgage expiry threats
            if re.search(r'mortgage.*expir.*lose.*nda|lose.*non.*disclosure|mortgage.*expir.*25.*abbots', 
                        body, re.IGNORECASE):
                key_findings['mortgage_expiry_threats'].append({
                    'date': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': subject,
                    'from': from_addr,
                    'context': extract_context(body, 'mortgage.*expir')
                })
            
            # Search for second mortgage offer
            if re.search(r'second.*mortgage|new.*mortgage.*offer|mortgage.*extension|£\d+.*mortgage.*fee', 
                        body, re.IGNORECASE):
                key_findings['second_mortgage_offer'].append({
                    'date': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': subject,
                    'from': from_addr,
                    'context': extract_context(body, 'mortgage')
                })
            
            # Search for mortgage fees
            if re.search(r'£\d{3,4}.*(?:fee|charge|cost).*mortgage|mortgage.*(?:fee|charge|cost).*£\d{3,4}', 
                        body, re.IGNORECASE):
                key_findings['mortgage_fees'].append({
                    'date': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': subject,
                    'from': from_addr,
                    'amount': extract_amounts(body)
                })
            
            # Search for urgent completion situations
            if 'urgent' in subject.lower() and re.search(r'complet|mortgage|exchange', body, re.IGNORECASE):
                key_findings['urgent_completion'].append({
                    'date': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': subject,
                    'from': from_addr,
                    'urgency_reason': extract_urgency_reason(body)
                })
        
        mbox.close()
    
    return key_findings

def extract_context(body, pattern):
    """Extract context around a pattern match."""
    lines = body.split('\n')
    context_lines = []
    
    for i, line in enumerate(lines):
        if re.search(pattern, line, re.IGNORECASE):
            # Get 2 lines before and after
            start = max(0, i-2)
            end = min(len(lines), i+3)
            context_lines.extend(lines[start:end])
    
    return '\n'.join(context_lines[:10])  # Limit to 10 lines

def extract_amounts(body):
    """Extract monetary amounts from body."""
    amounts = re.findall(r'£(\d{1,4}(?:,\d{3})*)', body)
    return list(set(amounts))  # Unique amounts

def extract_urgency_reason(body):
    """Extract why something is urgent."""
    urgency_keywords = ['deadline', 'expire', 'expiry', 'last day', 'final', 'must complete']
    
    lines = body.split('\n')
    for line in lines[:50]:  # Check first 50 lines
        if any(keyword in line.lower() for keyword in urgency_keywords):
            return line.strip()
    
    return "Urgent situation identified"

def display_findings(findings):
    """Display the key findings."""
    
    print("\n" + "="*80)
    print("MORTGAGE EXPIRY AND COMPLETION CRISIS - KEY EVIDENCE")
    print("="*80)
    
    # Mortgage expiry threats
    if findings['mortgage_expiry_threats']:
        print("\n🚨 MORTGAGE EXPIRY THREATS (NDA Leverage)")
        print("-"*80)
        for email in findings['mortgage_expiry_threats']:
            print(f"\n{email['date']} - {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Context:\n{email['context']}")
    
    # Second mortgage offer
    if findings['second_mortgage_offer']:
        print("\n💰 SECOND MORTGAGE OFFER / EXTENSION")
        print("-"*80)
        for email in findings['second_mortgage_offer'][:3]:
            print(f"\n{email['date']} - {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Context:\n{email['context']}")
    
    # Mortgage fees
    if findings['mortgage_fees']:
        print("\n💸 MORTGAGE FEES MENTIONED")
        print("-"*80)
        all_amounts = []
        for email in findings['mortgage_fees']:
            all_amounts.extend(email['amount'])
            print(f"\n{email['date']} - {email['subject']}")
            print(f"Amounts: £{', £'.join(email['amount'])}")
        
        print(f"\nTotal unique amounts mentioned: £{', £'.join(set(all_amounts))}")
    
    # Urgent completion situations
    if findings['urgent_completion']:
        print("\n🚨 URGENT COMPLETION SITUATIONS")
        print("-"*80)
        for email in findings['urgent_completion'][:5]:
            print(f"\n{email['date']} - {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Reason: {email['urgency_reason']}")
    
    # Jade's emails
    if findings['jade_emails']:
        print("\n📧 JADE'S EMAILS (Important Evidence)")
        print("-"*80)
        for email in findings['jade_emails'][:5]:
            print(f"\n{email['date']} - {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Preview: {email['excerpt'][:200]}...")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY OF FINDINGS")
    print("="*80)
    print(f"- Mortgage expiry threats: {len(findings['mortgage_expiry_threats'])} emails")
    print(f"- Second mortgage discussions: {len(findings['second_mortgage_offer'])} emails")
    print(f"- Mortgage fee mentions: {len(findings['mortgage_fees'])} emails")
    print(f"- Urgent completion situations: {len(findings['urgent_completion'])} emails")
    print(f"- Jade's relevant emails: {len(findings['jade_emails'])} emails")
    
    return findings

def main():
    findings = find_mortgage_crisis_emails()
    display_findings(findings)
    
    # Save findings
    import json
    with open('mortgage_crisis_findings.json', 'w') as f:
        json.dump(findings, f, indent=2)
    
    print("\n\nDetailed findings saved to mortgage_crisis_findings.json")

if __name__ == "__main__":
    main()