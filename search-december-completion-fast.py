#!/usr/bin/env python3
"""
Fast search for December 2023 completion emails - optimized version
"""

import mailbox
import email
from email.header import decode_header
from datetime import datetime
import re
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
    """Extract text content from email message - optimized version."""
    text_parts = []
    
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    text_parts.append(text[:5000])  # Limit text size
                except:
                    pass
    else:
        try:
            text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            text_parts.append(text[:5000])  # Limit text size
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

def quick_scan_mbox(mbox_path):
    """Quick scan focusing on subject lines and dates first."""
    print(f"\nQuick scanning {mbox_path}...")
    
    try:
        mbox = mailbox.mbox(mbox_path)
    except:
        print(f"Could not open {mbox_path}")
        return []
    
    relevant_emails = []
    processed = 0
    
    # Quick patterns for subject line
    quick_patterns = [
        r'completion',
        r'mortgage',
        r'december',
        r'urgent',
        r'plot.?34',
        r'10.?colt.?view',
        r'deadline',
        r'expir'
    ]
    
    for message in mbox:
        processed += 1
        if processed % 1000 == 0:
            print(f"  Processed {processed} emails...")
        
        # Quick date check
        date_str = message.get('Date', '')
        date_obj = parse_date(date_str)
        
        if not date_obj:
            continue
        
        # Only process Sept 2023 - Jan 2024
        if not ((date_obj.year == 2023 and date_obj.month >= 9) or 
                (date_obj.year == 2024 and date_obj.month == 1)):
            continue
        
        # Quick subject check
        subject = decode_header_value(message.get('Subject', '')).lower()
        
        # Check if subject matches any pattern
        if any(re.search(pattern, subject) for pattern in quick_patterns):
            # Get basic info
            from_addr = decode_header_value(message.get('From', ''))
            to_addr = decode_header_value(message.get('To', ''))
            
            # Check if involves relevant parties
            if any(domain in from_addr.lower() or domain in to_addr.lower() 
                   for domain in ['crestnicholson.com', 'bramsdonandchilds.co.uk', 'paulroberttaylor', 'jade.millington']):
                
                # Now get the body for detailed analysis
                body = extract_text_from_message(message)
                
                email_data = {
                    'date': date_obj,
                    'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': decode_header_value(message.get('Subject', '')),
                    'from': from_addr,
                    'to': to_addr,
                    'body': body
                }
                
                relevant_emails.append(email_data)
    
    mbox.close()
    print(f"  Found {len(relevant_emails)} potentially relevant emails")
    return relevant_emails

def analyze_completion_emails(emails):
    """Analyze emails for specific completion and mortgage issues."""
    
    # Categories
    mortgage_expiry = []
    completion_delays = []
    urgent_situations = []
    october_dates = []
    december_completion = []
    
    for email in emails:
        body_lower = email['body'].lower()
        subject_lower = email['subject'].lower()
        full_text = f"{subject_lower}\n{body_lower}"
        
        # Check for mortgage expiry
        if re.search(r'mortgage.*expir|expir.*mortgage|mortgage.*deadline|offer.*valid', full_text):
            mortgage_expiry.append(email)
        
        # Check for completion delays
        if re.search(r'completion.*delay|delay.*completion|postpone.*completion|completion.*moved', full_text):
            completion_delays.append(email)
        
        # Check for urgent situations
        if re.search(r'urgent|crisis|critical|asap|immediately', full_text):
            urgent_situations.append(email)
        
        # Check for October 25/31 mentions
        if re.search(r'october.*(25|31)|25.*october|31.*october', full_text):
            october_dates.append(email)
        
        # Check for December 18 completion
        if re.search(r'december.*18|18.*december|completion.*december', full_text):
            december_completion.append(email)
    
    return {
        'mortgage_expiry': mortgage_expiry,
        'completion_delays': completion_delays,
        'urgent_situations': urgent_situations,
        'october_dates': october_dates,
        'december_completion': december_completion
    }

def main():
    # Process both mbox files
    mbox_files = [
        "Crest-NHOS-Export.mbox",
        "Crest-NHOS-Export-001.mbox"
    ]
    
    all_emails = []
    
    for mbox_file in mbox_files:
        emails = quick_scan_mbox(mbox_file)
        all_emails.extend(emails)
    
    print(f"\nTotal relevant emails found: {len(all_emails)}")
    
    # Sort by date string to avoid timezone issues
    all_emails.sort(key=lambda x: x['date_str'])
    
    # Analyze categories
    categories = analyze_completion_emails(all_emails)
    
    # Display results
    print("\n" + "="*80)
    print("DECEMBER 2023 COMPLETION ANALYSIS")
    print("="*80)
    
    print(f"\nMortgage expiry discussions: {len(categories['mortgage_expiry'])}")
    print(f"Completion delay emails: {len(categories['completion_delays'])}")
    print(f"Urgent situations: {len(categories['urgent_situations'])}")
    print(f"October 25/31 discussions: {len(categories['october_dates'])}")
    print(f"December completion emails: {len(categories['december_completion'])}")
    
    # Show mortgage expiry emails
    print("\n" + "="*80)
    print("MORTGAGE EXPIRY EMAILS")
    print("="*80)
    
    for email in categories['mortgage_expiry'][:5]:
        print(f"\n{email['date_str']} - {email['subject']}")
        print(f"From: {email['from']}")
        
        # Find expiry mentions
        lines = email['body'].split('\n')
        for line in lines:
            if re.search(r'expir|deadline|valid|mortgage.*offer', line, re.IGNORECASE):
                print(f">>> {line.strip()}")
    
    # Show completion delay discussions
    print("\n" + "="*80)
    print("COMPLETION DELAYS")
    print("="*80)
    
    for email in categories['completion_delays'][:5]:
        print(f"\n{email['date_str']} - {email['subject']}")
        print(f"From: {email['from']}")
        
        # Find delay context
        lines = email['body'].split('\n')
        for i, line in enumerate(lines):
            if re.search(r'delay|postpone|moved|completion', line, re.IGNORECASE):
                # Show context
                start = max(0, i-1)
                end = min(len(lines), i+2)
                for j in range(start, end):
                    if j == i:
                        print(f">>> {lines[j].strip()}")
                    else:
                        print(f"    {lines[j].strip()}")
                break
    
    # Show urgent situations
    print("\n" + "="*80)
    print("URGENT SITUATIONS")
    print("="*80)
    
    for email in categories['urgent_situations'][:5]:
        print(f"\n🚨 {email['date_str']} - {email['subject']}")
        print(f"From: {email['from']}")
        
        # Find urgent context
        lines = email['body'].split('\n')
        for line in lines[:20]:  # Check first 20 lines
            if re.search(r'urgent|crisis|critical|asap', line, re.IGNORECASE):
                print(f">>> {line.strip()}")
    
    # Show October date discussions
    print("\n" + "="*80)
    print("OCTOBER 25/31 DATE DISCUSSIONS")
    print("="*80)
    
    for email in categories['october_dates'][:5]:
        print(f"\n{email['date_str']} - {email['subject']}")
        print(f"From: {email['from']}")
        
        # Find date mentions
        lines = email['body'].split('\n')
        for line in lines:
            if re.search(r'october.*(25|31)|25.*october|31.*october', line, re.IGNORECASE):
                print(f">>> {line.strip()}")
    
    # Create timeline summary
    print("\n" + "="*80)
    print("COMPLETION TIMELINE (Sept 2023 - Jan 2024)")
    print("="*80)
    
    # Group by month
    timeline = {}
    for email in all_emails:
        month = email['date'].strftime('%Y-%m')
        if month not in timeline:
            timeline[month] = []
        timeline[month].append(email)
    
    for month in sorted(timeline.keys()):
        print(f"\n{month}: {len(timeline[month])} emails")
        
        # Show key emails for each month
        month_emails = sorted(timeline[month], key=lambda x: x['date'])
        for email in month_emails[:5]:
            # Mark type of email
            markers = []
            if email in categories['urgent_situations']:
                markers.append('🚨')
            if email in categories['mortgage_expiry']:
                markers.append('💰')
            if email in categories['completion_delays']:
                markers.append('⏰')
            
            marker_str = ' '.join(markers) if markers else '  '
            print(f"  {marker_str} {email['date_str']}: {email['subject'][:60]}")
    
    # Save results
    results = {
        'total_emails': len(all_emails),
        'categories': {
            'mortgage_expiry': len(categories['mortgage_expiry']),
            'completion_delays': len(categories['completion_delays']),
            'urgent_situations': len(categories['urgent_situations']),
            'october_dates': len(categories['october_dates']),
            'december_completion': len(categories['december_completion'])
        },
        'key_emails': []
    }
    
    # Add key emails to results
    for category_name, emails in categories.items():
        for email in emails[:3]:  # Top 3 from each category
            results['key_emails'].append({
                'category': category_name,
                'date': email['date_str'],
                'subject': email['subject'],
                'from': email['from']
            })
    
    with open('december_completion_summary.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to december_completion_summary.json")

if __name__ == "__main__":
    main()