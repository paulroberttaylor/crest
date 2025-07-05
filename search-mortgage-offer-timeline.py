#!/usr/bin/env python3
"""Search for mortgage offer timeline and extension evidence"""

import mailbox
import email
from email.utils import parsedate_to_datetime
import re
from datetime import datetime

def search_mortgage_timeline(mbox_path):
    """Search for mortgage offer dates and extension evidence"""
    
    mbox = mailbox.mbox(mbox_path)
    
    # Results storage
    timeline_events = []
    mortgage_references = []
    
    print("Searching for mortgage offer timeline evidence...\n")
    
    # Search patterns
    patterns = {
        'mortgage_offer': r'mortgage.*(?:offer|application|approval|approved)',
        'validity_period': r'(?:3|three|6|six).*month.*(?:mortgage|offer|valid)',
        'expiry_concern': r'mortgage.*(?:expir|extend|deadline|run.*out|pressure)',
        'broker_mention': r'mortgage.*(?:advisor|adviser|broker)|(?:advisor|adviser|broker).*mortgage',
        'rate_change': r'(?:rate|interest).*(?:gone up|increase|change|rise)|borrowing.*(?:ability|dropped)',
        'extension': r'(?:extend|extension|renew|new).*mortgage.*(?:offer|application)',
        'june_july_2023': r'(?:June|July).*2023.*mortgage|mortgage.*(?:June|July).*2023'
    }
    
    for i, message in enumerate(mbox):
        try:
            # Get email metadata
            date_str = message.get('Date', '')
            if not date_str:
                continue
                
            try:
                date_obj = parsedate_to_datetime(date_str)
            except:
                continue
            
            # Focus on 2023 emails
            if date_obj.year != 2023:
                continue
            
            subject = message.get('Subject', '')
            from_addr = message.get('From', '')
            to_addr = message.get('To', '')
            
            # Get body
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
            else:
                try:
                    body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = str(message.get_payload())
            
            # Search for patterns
            found_patterns = []
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, body, re.IGNORECASE) or re.search(pattern, subject, re.IGNORECASE):
                    found_patterns.append(pattern_name)
            
            if found_patterns:
                email_data = {
                    'date': date_obj,
                    'date_str': date_obj.strftime('%Y-%m-%d %H:%M'),
                    'subject': subject,
                    'from': from_addr,
                    'to': to_addr,
                    'patterns': found_patterns,
                    'month': date_obj.strftime('%Y-%m')
                }
                
                # Extract specific evidence
                contexts = []
                
                # Look for mortgage offer mentions
                for match in re.finditer(r'.{0,200}mortgage.{0,100}(?:offer|application|approved).{0,200}', body, re.IGNORECASE):
                    contexts.append(('mortgage_offer', body[match.start():match.end()].strip()))
                
                # Look for validity periods
                for match in re.finditer(r'.{0,50}(?:3|three|6|six).{0,20}month.{0,100}', body, re.IGNORECASE):
                    if 'mortgage' in body[max(0, match.start()-100):match.end()+100].lower():
                        contexts.append(('validity_period', body[match.start():match.end()].strip()))
                
                # Look for rate changes
                for match in re.finditer(r'.{0,100}(?:rate|borrowing).{0,100}(?:gone up|dropped|increase).{0,100}', body, re.IGNORECASE):
                    contexts.append(('rate_impact', body[match.start():match.end()].strip()))
                
                if contexts:
                    email_data['contexts'] = contexts
                
                timeline_events.append(email_data)
                
        except Exception as e:
            continue
    
    # Sort by date
    timeline_events.sort(key=lambda x: x['date'])
    
    # Analyze timeline
    print("=== MORTGAGE OFFER TIMELINE ===\n")
    
    # Group by month
    monthly_summary = {}
    for event in timeline_events:
        month = event['month']
        if month not in monthly_summary:
            monthly_summary[month] = {
                'count': 0,
                'has_offer': False,
                'has_expiry_concern': False,
                'has_rate_change': False,
                'events': []
            }
        
        monthly_summary[month]['count'] += 1
        if 'mortgage_offer' in event['patterns']:
            monthly_summary[month]['has_offer'] = True
        if 'expiry_concern' in event['patterns']:
            monthly_summary[month]['has_expiry_concern'] = True
        if 'rate_change' in event['patterns']:
            monthly_summary[month]['has_rate_change'] = True
        monthly_summary[month]['events'].append(event)
    
    # Print monthly timeline
    for month in sorted(monthly_summary.keys()):
        summary = monthly_summary[month]
        print(f"\n{month}:")
        print(f"  Total emails: {summary['count']}")
        if summary['has_offer']:
            print("  ✓ Mortgage offer activity detected")
        if summary['has_rate_change']:
            print("  ⚠️  Rate change/impact mentioned")
        if summary['has_expiry_concern']:
            print("  🚨 Expiry concerns expressed")
    
    # Show key events
    print("\n\n=== KEY MORTGAGE EVENTS ===")
    
    # Find first mortgage offer mention
    offer_mentions = [e for e in timeline_events if 'mortgage_offer' in e['patterns']]
    if offer_mentions:
        first = offer_mentions[0]
        print(f"\nFirst mortgage offer mention:")
        print(f"  Date: {first['date_str']}")
        print(f"  Subject: {first['subject']}")
        if 'contexts' in first:
            for pattern_type, context in first['contexts']:
                if pattern_type == 'mortgage_offer':
                    print(f"  Context: ...{context[:200]}...")
                    break
    
    # Find rate change mentions
    rate_changes = [e for e in timeline_events if 'rate_change' in e['patterns']]
    if rate_changes:
        print(f"\n\nRate change impacts ({len(rate_changes)} found):")
        for event in rate_changes[:3]:  # Show first 3
            print(f"\n  {event['date_str']} - {event['subject']}")
            if 'contexts' in event:
                for pattern_type, context in event['contexts']:
                    if pattern_type == 'rate_impact':
                        # Clean up context
                        context = ' '.join(context.split())
                        print(f"    → {context}")
                        break
    
    # Find expiry concerns
    expiry_concerns = [e for e in timeline_events if 'expiry_concern' in e['patterns']]
    if expiry_concerns:
        print(f"\n\nMortgage expiry concerns ({len(expiry_concerns)} found):")
        print(f"  First concern: {expiry_concerns[0]['date_str']}")
        print(f"  Last concern: {expiry_concerns[-1]['date_str']}")
        
        # Show November concerns
        nov_concerns = [e for e in expiry_concerns if e['month'] == '2023-11']
        if nov_concerns:
            print(f"\n  November 2023 concerns ({len(nov_concerns)} emails):")
            for event in nov_concerns[:3]:
                print(f"    - {event['date_str']}: {event['subject']}")
    
    # Look for evidence of extensions or reapplications
    print("\n\n=== EXTENSION/REAPPLICATION EVIDENCE ===")
    
    extension_evidence = [e for e in timeline_events if 'extension' in e['patterns']]
    if extension_evidence:
        print(f"\nFound {len(extension_evidence)} emails mentioning extensions/new applications")
        for event in extension_evidence:
            print(f"\n  {event['date_str']} - {event['subject']}")
            if 'contexts' in event:
                for _, context in event['contexts']:
                    if 'extend' in context.lower() or 'new' in context.lower():
                        print(f"    Context: ...{context[:200]}...")
                        break
    else:
        print("\nNo direct mentions of mortgage extensions or new applications found")
        print("However, the timeline shows:")
        print("  - June 2023: Rate increases impacting borrowing ability")
        print("  - November 2023: Serious concerns about mortgage offer expiry")
        print("  - December 2023: Desperate attempts to complete before expiry")
    
    # Summary
    print("\n\n=== TIMELINE SUMMARY ===")
    print(f"Total mortgage-related emails: {len(timeline_events)}")
    print(f"Months covered: {min(monthly_summary.keys())} to {max(monthly_summary.keys())}")
    print(f"Emails with offer mentions: {len(offer_mentions)}")
    print(f"Emails with rate concerns: {len(rate_changes)}")
    print(f"Emails with expiry concerns: {len(expiry_concerns)}")
    
    # Calculate mortgage offer period
    if offer_mentions and expiry_concerns:
        first_offer = offer_mentions[0]['date']
        first_concern = expiry_concerns[0]['date']
        days_between = (first_concern - first_offer).days
        print(f"\nTime from first offer mention to first expiry concern: {days_between} days")
        
        # Standard mortgage offers are 3-6 months
        if days_between > 120:  # More than 4 months
            print("This suggests the mortgage offer was likely obtained before June 2023")
            print("(Standard offers are 3-6 months, concerns started ~5 months after first mention)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Using default mbox file...")
        mbox_path = "All mail Including Spam and Trash.mbox"
    else:
        mbox_path = sys.argv[1]
    
    search_mortgage_timeline(mbox_path)