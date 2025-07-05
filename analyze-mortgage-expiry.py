#!/usr/bin/env python3
"""Analyze mortgage expiry threats in detail"""

import json
import re
from datetime import datetime

def analyze_mortgage_expiry():
    # Load the mortgage threat emails
    with open('mortgage_threat_emails.json', 'r') as f:
        data = json.load(f)
    
    print('=== MORTGAGE EXPIRY THREATS ANALYSIS ===\n')
    
    # Find emails mentioning mortgage expiry
    expiry_emails = []
    extension_evidence = []
    timeline = []
    
    # Handle both list and dict formats
    emails = data if isinstance(data, list) else data.get('emails', [])
    
    for email in emails:
        body = email.get('body', '').lower()
        date = email.get('date', '')
        
        if 'mortgage' in body:
            # Look for expiry/extension mentions
            if any(term in body for term in ['expir', 'extend', 'extension', 'deadline', 'validity', 'reappl']):
                expiry_emails.append(email)
                
                # Extract specific evidence
                evidence = {
                    'date': date,
                    'from': email.get('from', ''),
                    'subject': email.get('subject', ''),
                    'type': []
                }
                
                # Categorize the evidence
                if 'expir' in body:
                    evidence['type'].append('expiry_threat')
                if 'extend' in body or 'extension' in body:
                    evidence['type'].append('extension_needed')
                if 'deadline' in body:
                    evidence['type'].append('deadline_pressure')
                if 'reappl' in body or 'new application' in body:
                    evidence['type'].append('reapplication')
                
                # Extract context
                contexts = []
                patterns = [
                    r'.{0,150}mortgage.{0,50}expir.{0,150}',
                    r'.{0,150}mortgage.{0,50}extend.{0,150}',
                    r'.{0,150}mortgage.{0,50}deadline.{0,150}',
                    r'.{0,150}mortgage.{0,50}offer.{0,150}'
                ]
                
                for pattern in patterns:
                    for match in re.finditer(pattern, body):
                        context = email.get('body', '')[match.start():match.end()].strip()
                        contexts.append(context)
                
                if contexts:
                    evidence['contexts'] = contexts
                    extension_evidence.append(evidence)
            
            # Add to timeline
            timeline.append({
                'date': date,
                'subject': email.get('subject', ''),
                'has_expiry_concern': any(term in body for term in ['expir', 'extend', 'deadline'])
            })
    
    # Sort by date
    expiry_emails.sort(key=lambda x: x.get('date', ''))
    extension_evidence.sort(key=lambda x: x.get('date', ''))
    timeline.sort(key=lambda x: x.get('date', ''))
    
    print(f'Found {len(expiry_emails)} emails mentioning mortgage expiry/extension concerns\n')
    
    # Show detailed evidence
    print('=== KEY MORTGAGE EXPIRY EVIDENCE ===\n')
    
    for evidence in extension_evidence[:15]:  # Show first 15
        print(f"Date: {evidence['date']}")
        print(f"From: {evidence['from']}")
        print(f"Subject: {evidence['subject']}")
        print(f"Evidence Type: {', '.join(evidence['type'])}")
        
        if 'contexts' in evidence:
            print("\nKey Contexts:")
            for i, context in enumerate(evidence['contexts'][:2]):  # Show first 2 contexts
                # Clean up the context
                context = ' '.join(context.split())
                print(f"  {i+1}. ...{context}...")
        
        print('-' * 80)
    
    # Analyze timeline
    print('\n=== MORTGAGE TIMELINE ANALYSIS ===\n')
    
    # Find first and last mentions
    if timeline:
        first_mention = timeline[0]
        last_mention = timeline[-1]
        
        print(f"First mortgage email: {first_mention['date']} - {first_mention['subject']}")
        print(f"Last mortgage email: {last_mention['date']} - {last_mention['subject']}")
        
        # Count emails by month
        monthly_counts = {}
        expiry_concerns_by_month = {}
        
        for item in timeline:
            date_str = item['date']
            if date_str:
                try:
                    # Parse date to get month
                    month = date_str[:7]  # YYYY-MM format
                    monthly_counts[month] = monthly_counts.get(month, 0) + 1
                    
                    if item['has_expiry_concern']:
                        expiry_concerns_by_month[month] = expiry_concerns_by_month.get(month, 0) + 1
                except:
                    pass
        
        print("\nMortgage emails by month:")
        for month in sorted(monthly_counts.keys()):
            expiry_count = expiry_concerns_by_month.get(month, 0)
            print(f"  {month}: {monthly_counts[month]} emails ({expiry_count} with expiry concerns)")
    
    # Look for specific dates mentioned
    print('\n=== SPECIFIC MORTGAGE DATES MENTIONED ===\n')
    
    date_patterns = [
        (r'mortgage.{0,50}(?:June|July|August|September|October|November|December).{0,10}2023', 'mortgage_date'),
        (r'(?:3|three).{0,10}month.{0,30}mortgage', '3_month_mortgage'),
        (r'(?:6|six).{0,10}month.{0,30}mortgage', '6_month_mortgage'),
        (r'mortgage.{0,30}(?:valid|expir).{0,50}', 'validity_mention')
    ]
    
    date_mentions = []
    for email in emails:
        body = email.get('body', '')
        
        for pattern, pattern_type in date_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                date_mentions.append({
                    'date': email.get('date', ''),
                    'type': pattern_type,
                    'matches': matches[:2]  # First 2 matches
                })
    
    if date_mentions:
        for mention in date_mentions[:10]:
            print(f"{mention['date']} - {mention['type']}: {mention['matches']}")
    
    # Save detailed analysis
    results = {
        'total_mortgage_emails': len(timeline),
        'emails_with_expiry_concerns': len(expiry_emails),
        'detailed_evidence': extension_evidence,
        'timeline_summary': {
            'first_email': timeline[0] if timeline else None,
            'last_email': timeline[-1] if timeline else None,
            'monthly_counts': monthly_counts,
            'expiry_concerns_by_month': expiry_concerns_by_month
        }
    }
    
    with open('mortgage_expiry_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nDetailed analysis saved to mortgage_expiry_analysis.json")
    
    # Final summary
    print("\n=== SUMMARY OF FINDINGS ===")
    print(f"1. Total mortgage-related emails: {len(timeline)}")
    print(f"2. Emails expressing expiry concerns: {len(expiry_emails)}")
    print(f"3. Months with highest expiry concerns: {max(expiry_concerns_by_month.items(), key=lambda x: x[1])[0] if expiry_concerns_by_month else 'None'}")
    
    # Look for evidence of second application
    second_app_count = sum(1 for e in extension_evidence if 'reapplication' in e.get('type', []))
    if second_app_count > 0:
        print(f"4. Evidence of mortgage reapplication: YES ({second_app_count} emails)")
    else:
        print("4. Evidence of mortgage reapplication: Not found in email subjects/bodies")

if __name__ == "__main__":
    analyze_mortgage_expiry()