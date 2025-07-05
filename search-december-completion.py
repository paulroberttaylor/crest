#!/usr/bin/env python3
"""
Search MBOX files for emails related to December 2023 completion of Plot 34/10 Colt View
Focus on: completion delays, mortgage expiry issues, urgent situations
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

def analyze_mbox(mbox_path):
    """Analyze a single mbox file for completion-related emails."""
    print(f"\nAnalyzing {mbox_path}...")
    
    try:
        mbox = mailbox.mbox(mbox_path)
    except:
        print(f"Could not open {mbox_path}")
        return []
    
    completion_emails = []
    
    # Search patterns for December completion issues
    completion_patterns = [
        r'completion.*december|december.*completion',
        r'completion.*delay|delay.*completion',
        r'mortgage.*expir|expir.*mortgage',
        r'mortgage.*offer.*expir',
        r'urgent.*completion|completion.*urgent',
        r'crisis|critical.*situation',
        r'exchange.*complet',
        r'completion.*date',
        r'december.*18|18.*december',
        r'plot.*34|10.*colt.*view',
        r'mortgage.*deadline',
        r'completion.*deadline',
        r'mortgage.*extension',
        r'completion.*risk'
    ]
    
    # Key people involved
    key_people = ['paul', 'jade', 'crest', '@crestnicholson.com', '@bramsdonandchilds.co.uk']
    
    for i, message in enumerate(mbox):
        # Get date
        date_str = message.get('Date', '')
        date_obj = parse_date(date_str)
        
        if not date_obj:
            continue
        
        # Focus on emails from September-December 2023 (completion period)
        if not (date_obj.year == 2023 and date_obj.month >= 9) and not (date_obj.year == 2024 and date_obj.month == 1):
            continue
        
        # Get headers
        subject = decode_header_value(message.get('Subject', ''))
        from_addr = decode_header_value(message.get('From', ''))
        to_addr = decode_header_value(message.get('To', ''))
        cc_addr = decode_header_value(message.get('Cc', ''))
        
        # Get body
        body = extract_text_from_message(message)
        full_content = f"{subject}\n{body}".lower()
        
        # Check if relevant to completion/mortgage issues
        is_relevant = False
        matched_patterns = []
        
        for pattern in completion_patterns:
            if re.search(pattern, full_content, re.IGNORECASE):
                is_relevant = True
                matched_patterns.append(pattern)
        
        # Also check if involves key people
        people_involved = any(person in from_addr.lower() or person in to_addr.lower() 
                            for person in key_people)
        
        if is_relevant and people_involved:
            # Extract key phrases
            urgency_level = 'normal'
            if any(word in full_content for word in ['urgent', 'crisis', 'critical', 'asap', 'immediately']):
                urgency_level = 'high'
            
            email_data = {
                'date': date_obj,
                'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'cc': cc_addr,
                'urgency': urgency_level,
                'matched_patterns': matched_patterns,
                'body_preview': body[:2000],  # First 2000 chars
                'full_body': body
            }
            
            completion_emails.append(email_data)
    
    mbox.close()
    return completion_emails

def find_mortgage_expiry_mentions(emails):
    """Find specific mentions of mortgage expiry dates and issues."""
    mortgage_expiry_emails = []
    
    expiry_patterns = [
        r'mortgage.*expir.*(\d{1,2}.*(?:january|february|december|november)|\d{1,2}/\d{1,2})',
        r'offer.*valid.*until',
        r'mortgage.*deadline',
        r'£\d+.*(?:fee|cost|charge).*mortgage',
        r'second.*mortgage.*offer',
        r'mortgage.*extension',
        r'rate.*increase',
        r'interest.*rate.*change'
    ]
    
    for email in emails:
        body = email['full_body']
        
        for pattern in expiry_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                email['mortgage_expiry_mentions'] = matches
                mortgage_expiry_emails.append(email)
                break
    
    return mortgage_expiry_emails

def find_completion_date_changes(emails):
    """Find emails discussing changes to the completion date."""
    date_change_emails = []
    
    date_patterns = [
        r'completion.*(?:moved|changed|delayed|postponed)',
        r'new.*completion.*date',
        r'completion.*now.*(\d{1,2}.*(?:december|january))',
        r'unable.*complete.*(?:october|november)',
        r'october.*31|31.*october',
        r'october.*25|25.*october',
        r'december.*18|18.*december'
    ]
    
    for email in emails:
        body = email['full_body']
        
        for pattern in date_patterns:
            if re.search(pattern, body, re.IGNORECASE):
                # Extract context around date mentions
                lines = body.split('\n')
                relevant_lines = []
                
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Get surrounding context
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        relevant_lines.extend(lines[start:end])
                
                email['date_change_context'] = '\n'.join(relevant_lines)
                date_change_emails.append(email)
                break
    
    return date_change_emails

def main():
    # Analyze both mbox files
    mbox_files = [
        "Crest-NHOS-Export.mbox",
        "Crest-NHOS-Export-001.mbox"
    ]
    
    all_completion_emails = []
    
    for mbox_file in mbox_files:
        emails = analyze_mbox(mbox_file)
        all_completion_emails.extend(emails)
    
    print(f"\nTotal completion-related emails found: {len(all_completion_emails)}")
    
    # Sort by date
    all_completion_emails.sort(key=lambda x: x['date'])
    
    # Find mortgage expiry mentions
    mortgage_expiry_emails = find_mortgage_expiry_mentions(all_completion_emails)
    
    # Find completion date change discussions
    date_change_emails = find_completion_date_changes(all_completion_emails)
    
    # Display results
    print("\n" + "="*80)
    print("DECEMBER 2023 COMPLETION TIMELINE")
    print("="*80)
    
    # Group by month
    months = {}
    for email in all_completion_emails:
        month_key = email['date'].strftime('%Y-%m')
        if month_key not in months:
            months[month_key] = []
        months[month_key].append(email)
    
    for month, emails in sorted(months.items()):
        print(f"\n{month} ({len(emails)} emails)")
        print("-"*40)
        
        for email in emails[:10]:  # Show first 10 per month
            urgency_marker = "🚨 " if email['urgency'] == 'high' else ""
            print(f"{urgency_marker}{email['date_str']} - {email['subject']}")
            print(f"   From: {email['from']}")
            if 'mortgage' in email['subject'].lower() or 'mortgage' in str(email.get('matched_patterns', [])):
                print("   [MORTGAGE RELATED]")
    
    # Display mortgage expiry issues
    print("\n" + "="*80)
    print("MORTGAGE EXPIRY DISCUSSIONS")
    print("="*80)
    
    for email in mortgage_expiry_emails[:10]:
        print(f"\nDate: {email['date_str']}")
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        if 'mortgage_expiry_mentions' in email:
            print(f"Mentions: {email['mortgage_expiry_mentions']}")
        
        # Find relevant excerpt
        lines = email['full_body'].split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['expir', 'deadline', 'valid until', 'fee']):
                print(f"\nRelevant excerpt: {line.strip()}")
                break
    
    # Display completion date changes
    print("\n" + "="*80)
    print("COMPLETION DATE CHANGE DISCUSSIONS")
    print("="*80)
    
    for email in date_change_emails[:10]:
        print(f"\nDate: {email['date_str']}")
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        
        if 'date_change_context' in email:
            print("\nContext:")
            print("-"*40)
            print(email['date_change_context'][:500])
    
    # Look for crisis/urgent situations
    print("\n" + "="*80)
    print("URGENT/CRISIS SITUATIONS")
    print("="*80)
    
    urgent_emails = [e for e in all_completion_emails if e['urgency'] == 'high']
    
    for email in urgent_emails[:10]:
        print(f"\n🚨 {email['date_str']} - {email['subject']}")
        print(f"From: {email['from']}")
        
        # Find urgent context
        lines = email['full_body'].split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['urgent', 'crisis', 'critical', 'immediately']):
                print(f"Context: {line.strip()}")
                break
    
    # Save detailed results
    results = {
        'total_emails': len(all_completion_emails),
        'mortgage_expiry_emails': len(mortgage_expiry_emails),
        'date_change_emails': len(date_change_emails),
        'urgent_emails': len(urgent_emails),
        'timeline': []
    }
    
    # Create detailed timeline
    for email in all_completion_emails:
        results['timeline'].append({
            'date': email['date_str'],
            'subject': email['subject'],
            'from': email['from'],
            'urgency': email['urgency'],
            'type': 'mortgage' if 'mortgage' in str(email['matched_patterns']) else 'completion'
        })
    
    with open('december_completion_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nDetailed results saved to december_completion_analysis.json")
    
    # Create a focused summary
    print("\n" + "="*80)
    print("KEY FINDINGS SUMMARY")
    print("="*80)
    
    print(f"\n1. Total completion-related emails: {len(all_completion_emails)}")
    print(f"2. Mortgage expiry discussions: {len(mortgage_expiry_emails)}")
    print(f"3. Completion date changes: {len(date_change_emails)}")
    print(f"4. Urgent/crisis situations: {len(urgent_emails)}")
    
    # Look for specific October 25/31 discussions
    oct_25_31_emails = []
    for email in all_completion_emails:
        if re.search(r'october.*(25|31)|31.*october|25.*october', email['full_body'], re.IGNORECASE):
            oct_25_31_emails.append(email)
    
    if oct_25_31_emails:
        print(f"\n5. October 25/31 date discussions: {len(oct_25_31_emails)} emails")
        print("   Key emails:")
        for email in oct_25_31_emails[:3]:
            print(f"   - {email['date_str']}: {email['subject']}")

if __name__ == "__main__":
    main()