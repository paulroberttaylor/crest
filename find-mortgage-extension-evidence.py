#!/usr/bin/env python3
"""Find specific evidence of mortgage extensions and second applications due to Crest delays"""

import json
import mailbox
import email
from email.utils import parsedate_to_datetime
from datetime import datetime
import re

def search_mortgage_evidence(mbox_path):
    """Search for mortgage extension and reapplication evidence"""
    
    mbox = mailbox.mbox(mbox_path)
    results = {
        'mortgage_timeline': [],
        'extension_evidence': [],
        'financial_impact': [],
        'broker_references': [],
        'key_findings': {}
    }
    
    # Keywords to search for
    mortgage_keywords = [
        r'mortgage.*(?:expire|expiry|extend|extension)',
        r'mortgage.*(?:offer.*valid|validity)',
        r'mortgage.*(?:deadline|pressure)',
        r'(?:second|new|another).*mortgage.*(?:application|offer)',
        r'mortgage.*(?:reappl|re-appl|again)',
        r'mortgage.*(?:workshop|broker|advisor)',
        r'(?:fee|cost|charge).*mortgage',
        r'mortgage.*(?:arrangement|valuation)',
        r'3.*month.*mortgage',
        r'6.*month.*mortgage',
        r'mortgage.*(?:June|July|August|September|October|November|December).*2023'
    ]
    
    print("Searching for mortgage extension evidence...")
    
    for i, message in enumerate(mbox):
        try:
            # Get email metadata
            date_str = message.get('Date', '')
            if date_str:
                try:
                    date_obj = parsedate_to_datetime(date_str)
                except:
                    continue
            else:
                continue
            
            # Only 2023 emails
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
            
            # Search for mortgage evidence
            body_lower = body.lower()
            subject_lower = subject.lower()
            
            # Check for mortgage keywords
            found_keywords = []
            for pattern in mortgage_keywords:
                if re.search(pattern, body_lower, re.IGNORECASE) or re.search(pattern, subject_lower, re.IGNORECASE):
                    found_keywords.append(pattern)
            
            if found_keywords:
                email_data = {
                    'date': date_obj.isoformat(),
                    'subject': subject,
                    'from': from_addr,
                    'to': to_addr,
                    'keywords': found_keywords
                }
                
                # Extract specific evidence
                if re.search(r'mortgage.*(?:expire|expiry|extend)', body_lower):
                    # Find context around expiry mentions
                    for match in re.finditer(r'.{0,200}mortgage.{0,50}(?:expire|expiry|extend).{0,200}', body_lower):
                        email_data['expiry_context'] = body[match.start():match.end()].strip()
                        results['extension_evidence'].append(email_data)
                        print(f"\nFound mortgage expiry evidence - {date_obj.strftime('%Y-%m-%d')}")
                        print(f"From: {from_addr}")
                        print(f"Context: {email_data['expiry_context'][:200]}...")
                
                # Look for broker/workshop references
                if re.search(r'mortgage.*workshop|leanne|broker', body_lower):
                    results['broker_references'].append(email_data)
                    # Extract broker context
                    for match in re.finditer(r'.{0,200}(?:mortgage.*workshop|leanne|broker).{0,200}', body_lower):
                        print(f"\nFound broker reference - {date_obj.strftime('%Y-%m-%d')}")
                        print(f"Context: {body[match.start():match.end()].strip()[:200]}...")
                
                # Look for fees/costs
                if re.search(r'(?:£\d+|fee|cost|charge).*mortgage|mortgage.*(?:£\d+|fee|cost|charge)', body_lower):
                    # Extract fee amounts
                    fee_matches = re.findall(r'£(\d+(?:,\d{3})*(?:\.\d{2})?)', body)
                    if fee_matches:
                        email_data['fees'] = fee_matches
                        results['financial_impact'].append(email_data)
                        print(f"\nFound mortgage fee reference - {date_obj.strftime('%Y-%m-%d')}")
                        print(f"Fees found: {fee_matches}")
                
                # Add to timeline
                results['mortgage_timeline'].append(email_data)
                
        except Exception as e:
            continue
    
    # Sort timeline
    results['mortgage_timeline'].sort(key=lambda x: x['date'])
    
    # Analyze findings
    print("\n\n=== MORTGAGE TIMELINE ANALYSIS ===")
    
    # Look for patterns
    first_mortgage_ref = None
    last_mortgage_ref = None
    expiry_mentions = []
    
    for email in results['mortgage_timeline']:
        if not first_mortgage_ref:
            first_mortgage_ref = email['date']
        last_mortgage_ref = email['date']
        
        if 'expiry_context' in email:
            expiry_mentions.append({
                'date': email['date'],
                'context': email.get('expiry_context', '')
            })
    
    results['key_findings'] = {
        'first_mortgage_reference': first_mortgage_ref,
        'last_mortgage_reference': last_mortgage_ref,
        'total_mortgage_emails': len(results['mortgage_timeline']),
        'expiry_concern_emails': len(results['extension_evidence']),
        'broker_emails': len(results['broker_references']),
        'financial_impact_emails': len(results['financial_impact']),
        'expiry_mentions': expiry_mentions
    }
    
    # Print summary
    print(f"\nFirst mortgage reference: {first_mortgage_ref}")
    print(f"Last mortgage reference: {last_mortgage_ref}")
    print(f"Total mortgage-related emails: {len(results['mortgage_timeline'])}")
    print(f"Emails mentioning expiry/extension: {len(results['extension_evidence'])}")
    print(f"Emails with broker references: {len(results['broker_references'])}")
    print(f"Emails with financial impact: {len(results['financial_impact'])}")
    
    if expiry_mentions:
        print("\n=== MORTGAGE EXPIRY CONCERNS ===")
        for mention in expiry_mentions:
            print(f"\n{mention['date']}: {mention['context'][:300]}...")
    
    # Save detailed results
    with open('mortgage_extension_evidence.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nDetailed results saved to mortgage_extension_evidence.json")
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Searching default mbox file...")
        mbox_path = "All mail Including Spam and Trash.mbox"
    else:
        mbox_path = sys.argv[1]
    
    search_mortgage_evidence(mbox_path)