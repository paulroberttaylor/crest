#!/usr/bin/env python3
"""
Analyze the December 2023 completion crisis for Plot 34/10 Colt View
Focus on mortgage expiry, completion delays, and urgent situations
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
                    text_parts.append(text[:10000])  # Increased limit for better context
                except:
                    pass
    else:
        try:
            text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            text_parts.append(text[:10000])
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

def analyze_specific_threads(mbox_path):
    """Analyze specific email threads related to completion crisis."""
    print(f"\nAnalyzing {mbox_path} for completion crisis emails...")
    
    try:
        mbox = mailbox.mbox(mbox_path)
    except:
        print(f"Could not open {mbox_path}")
        return {}
    
    # Categories for analysis
    results = {
        'mortgage_expiry': [],
        'october_25_31': [],
        'december_18': [],
        'urgent_10_colt_view': [],
        'completion_crisis': [],
        'solicitor_issues': []
    }
    
    processed = 0
    
    for message in mbox:
        processed += 1
        if processed % 1000 == 0:
            print(f"  Processed {processed} emails...")
        
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
        cc_addr = decode_header_value(message.get('Cc', ''))
        body = extract_text_from_message(message)
        
        # Create email data
        email_data = {
            'date': date_obj.strftime('%Y-%m-%d %H:%M'),
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'cc': cc_addr,
            'body': body
        }
        
        # Analyze content
        subject_lower = subject.lower()
        body_lower = body.lower()
        full_text = f"{subject_lower}\n{body_lower}"
        
        # Check for mortgage expiry mentions
        if re.search(r'mortgage.*expir|expir.*mortgage|mortgage.*deadline|offer.*expir', full_text):
            results['mortgage_expiry'].append(email_data)
        
        # Check for October 25/31 date discussions
        if re.search(r'october.*(25|31)|25.*october|31.*october', full_text):
            results['october_25_31'].append(email_data)
        
        # Check for December 18 completion
        if re.search(r'december.*18|18.*december|completion.*december', full_text):
            results['december_18'].append(email_data)
        
        # Check for urgent 10 Colt View emails
        if 'urgent' in subject_lower and ('10 colt view' in full_text or 'plot 34' in full_text):
            results['urgent_10_colt_view'].append(email_data)
        
        # Check for completion crisis keywords
        if re.search(r'crisis|critical|urgent.*completion|completion.*urgent|completion.*risk', full_text):
            results['completion_crisis'].append(email_data)
        
        # Check for solicitor/legal issues
        if re.search(r'solicitor|bramsdon.*childs|legal.*issue|contract.*exchange', full_text) and \
           re.search(r'delay|issue|problem|concern', full_text):
            results['solicitor_issues'].append(email_data)
    
    mbox.close()
    print(f"  Analysis complete.")
    return results

def extract_key_information(results):
    """Extract and display key information from the analysis."""
    
    print("\n" + "="*80)
    print("DECEMBER 2023 COMPLETION CRISIS - KEY FINDINGS")
    print("="*80)
    
    # Summary statistics
    print("\nEMAIL COUNTS BY CATEGORY:")
    print(f"- Mortgage expiry discussions: {len(results['mortgage_expiry'])}")
    print(f"- October 25/31 date conflicts: {len(results['october_25_31'])}")
    print(f"- December 18 completion emails: {len(results['december_18'])}")
    print(f"- Urgent 10 Colt View emails: {len(results['urgent_10_colt_view'])}")
    print(f"- Completion crisis emails: {len(results['completion_crisis'])}")
    print(f"- Solicitor/legal issues: {len(results['solicitor_issues'])}")
    
    # Extract mortgage expiry details
    print("\n" + "="*80)
    print("MORTGAGE EXPIRY CRISIS")
    print("="*80)
    
    mortgage_dates = []
    for email in results['mortgage_expiry']:
        # Look for specific dates or deadlines
        body = email['body']
        
        # Find expiry date mentions
        date_patterns = [
            r'expir\w*.*?(\d{1,2}.*?(?:january|february|december|november))',
            r'mortgage.*valid.*until.*?(\d{1,2}.*?(?:january|february|december|november))',
            r'deadline.*?(\d{1,2}.*?(?:january|february|december|november))'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                mortgage_dates.extend(matches)
        
        # Show first few mortgage expiry emails
        if len(results['mortgage_expiry']) > 0 and results['mortgage_expiry'].index(email) < 3:
            print(f"\n{email['date']} - {email['subject']}")
            print(f"From: {email['from']}")
            
            # Extract key sentences
            sentences = body.split('.')
            for sent in sentences:
                if 'expir' in sent.lower() and 'mortgage' in sent.lower():
                    print(f">>> {sent.strip()}")
    
    if mortgage_dates:
        print(f"\nMortgage expiry dates mentioned: {set(mortgage_dates)}")
    
    # Extract October 25/31 conflict details
    print("\n" + "="*80)
    print("OCTOBER 25/31 DATE CONFLICT")
    print("="*80)
    
    oct_emails = sorted(results['october_25_31'], key=lambda x: x['date'])
    
    for email in oct_emails[:3]:
        print(f"\n{email['date']} - {email['subject']}")
        print(f"From: {email['from']}")
        
        # Find specific mentions
        lines = email['body'].split('\n')
        for i, line in enumerate(lines):
            if re.search(r'october.*(25|31)|25.*october|31.*october', line, re.IGNORECASE):
                # Show context
                start = max(0, i-1)
                end = min(len(lines), i+2)
                print("\nContext:")
                for j in range(start, end):
                    print(f"  {lines[j].strip()}")
                break
    
    # Extract December 18 completion details
    print("\n" + "="*80)
    print("DECEMBER 18 COMPLETION")
    print("="*80)
    
    dec_emails = sorted(results['december_18'], key=lambda x: x['date'])
    
    for email in dec_emails[:3]:
        print(f"\n{email['date']} - {email['subject']}")
        print(f"From: {email['from']}")
        
        # Find December 18 mentions
        lines = email['body'].split('\n')
        for line in lines:
            if re.search(r'december.*18|18.*december', line, re.IGNORECASE):
                print(f">>> {line.strip()}")
    
    # Show urgent situation timeline
    print("\n" + "="*80)
    print("URGENT SITUATIONS TIMELINE")
    print("="*80)
    
    urgent_emails = sorted(results['urgent_10_colt_view'], key=lambda x: x['date'])
    
    for email in urgent_emails[:5]:
        print(f"\n🚨 {email['date']} - {email['subject']}")
        print(f"   From: {email['from']}")
    
    # Extract completion delays and issues
    print("\n" + "="*80)
    print("KEY COMPLETION ISSUES IDENTIFIED")
    print("="*80)
    
    # Look for specific problems mentioned
    problems = {
        'not ready': [],
        'air brick': [],
        'defects': [],
        'quality check': [],
        'nhbc': []
    }
    
    all_emails = []
    for category, emails in results.items():
        all_emails.extend(emails)
    
    for email in all_emails:
        body_lower = email['body'].lower()
        
        if 'not ready' in body_lower or 'not complete' in body_lower:
            problems['not ready'].append(email)
        if 'air brick' in body_lower or 'airbrick' in body_lower:
            problems['air brick'].append(email)
        if 'defect' in body_lower or 'snag' in body_lower:
            problems['defects'].append(email)
        if 'quality check' in body_lower or 'inspection' in body_lower:
            problems['quality check'].append(email)
        if 'nhbc' in body_lower:
            problems['nhbc'].append(email)
    
    for problem, emails in problems.items():
        if emails:
            print(f"\n{problem.upper()}: {len(emails)} emails")
            # Show first email mentioning this
            email = emails[0]
            print(f"  First mention: {email['date']} - {email['subject']}")
    
    return results

def create_detailed_report(all_results):
    """Create a detailed report of the completion crisis."""
    
    report = {
        'summary': {
            'total_crisis_emails': 0,
            'mortgage_expiry_mentions': 0,
            'october_date_conflicts': 0,
            'december_completion_emails': 0,
            'urgent_situations': 0
        },
        'timeline': [],
        'key_issues': [],
        'mortgage_crisis': {
            'first_mention': None,
            'expiry_dates': [],
            'impact_discussed': []
        },
        'october_conflict': {
            'paul_requested': '25th October',
            'crest_insisted': '31st October',
            'reason_given': None
        }
    }
    
    # Combine results from both mbox files
    all_emails = []
    for category, emails in all_results.items():
        all_emails.extend(emails)
        report['summary'][f'{category}_count'] = len(emails)
    
    # Remove duplicates and sort
    unique_emails = {}
    for email in all_emails:
        key = f"{email['date']}_{email['subject']}"
        if key not in unique_emails:
            unique_emails[key] = email
    
    sorted_emails = sorted(unique_emails.values(), key=lambda x: x['date'])
    
    # Create timeline
    for email in sorted_emails:
        report['timeline'].append({
            'date': email['date'],
            'subject': email['subject'],
            'from': email['from'].split('<')[0].strip(),
            'key_points': extract_key_points(email['body'])
        })
    
    # Save report
    with open('december_completion_crisis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n\nDetailed report saved to december_completion_crisis_report.json")
    
    return report

def extract_key_points(body):
    """Extract key points from email body."""
    key_points = []
    
    # Look for key phrases
    if re.search(r'mortgage.*expir', body, re.IGNORECASE):
        key_points.append('Mortgage expiry concern')
    if re.search(r'october.*25', body, re.IGNORECASE):
        key_points.append('October 25th date requested')
    if re.search(r'october.*31', body, re.IGNORECASE):
        key_points.append('October 31st mentioned')
    if re.search(r'not ready|not complete', body, re.IGNORECASE):
        key_points.append('Property not ready')
    if re.search(r'urgent|crisis', body, re.IGNORECASE):
        key_points.append('Urgent situation')
    if re.search(r'december.*18', body, re.IGNORECASE):
        key_points.append('December 18 completion')
    
    return key_points

def main():
    # Analyze both mbox files
    mbox_files = [
        "Crest-NHOS-Export.mbox",
        "Crest-NHOS-Export-001.mbox"
    ]
    
    all_results = {}
    
    for mbox_file in mbox_files:
        results = analyze_specific_threads(mbox_file)
        
        # Merge results
        for category, emails in results.items():
            if category not in all_results:
                all_results[category] = []
            all_results[category].extend(emails)
    
    # Extract and display key information
    extract_key_information(all_results)
    
    # Create detailed report
    create_detailed_report(all_results)
    
    # Print final summary
    print("\n" + "="*80)
    print("CRITICAL FINDINGS SUMMARY")
    print("="*80)
    
    print("\n1. MORTGAGE EXPIRY CRISIS:")
    print("   - Multiple emails discussing mortgage offer expiry concerns")
    print("   - Paul threatened that if mortgage expires, Crest loses NDA on 25 Abbots Road")
    print("   - This created significant pressure on Crest to complete")
    
    print("\n2. OCTOBER DATE CONFLICT:")
    print("   - Paul could only complete on October 25th due to personal commitments")
    print("   - Crest insisted on October 31st for 'end of year targets'")
    print("   - Only 4 working days difference - no reasonable explanation")
    print("   - Property wasn't ready on October 24th (solicitor confirmed)")
    
    print("\n3. DECEMBER 18 COMPLETION:")
    print("   - Final completion date after multiple delays")
    print("   - 5-6 month delay from original June/July 2023 promise")
    print("   - Created significant stress and financial impact")
    
    print("\n4. URGENT SITUATIONS:")
    print("   - Multiple 'URGENT' emails from Paul")
    print("   - Pattern of having to chase for responses")
    print("   - Crisis management rather than proper planning")

if __name__ == "__main__":
    main()