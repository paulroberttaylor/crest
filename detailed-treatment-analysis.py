#!/usr/bin/env python3
"""
Detailed analysis of how Paul and Jade were treated during Plot 34 purchase.
Focuses on specific evidence of poor treatment, broken promises, delays.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

def parse_date(date_str):
    """Parse ISO date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None

def calculate_response_time(date1_str, date2_str):
    """Calculate days between two dates."""
    date1 = parse_date(date1_str)
    date2 = parse_date(date2_str)
    if date1 and date2:
        return abs((date2 - date1).days)
    return None

def analyze_complaint_pattern(emails):
    """Analyze the pattern of complaints and responses."""
    complaint_pattern = {
        'total_complaints': 0,
        'acknowledgements': [],
        'pathways': [],
        'assessments': [],
        'interim_updates': [],
        'final_responses': [],
        'response_delays': [],
        'unresolved_issues': []
    }
    
    for email in emails:
        subject_lower = email['subject'].lower()
        
        if 'acknowledgement' in subject_lower:
            complaint_pattern['acknowledgements'].append(email)
        elif 'pathway' in subject_lower:
            complaint_pattern['pathways'].append(email)
        elif 'assessment' in subject_lower:
            complaint_pattern['assessments'].append(email)
        elif 'interim' in subject_lower:
            complaint_pattern['interim_updates'].append(email)
        elif 'final' in subject_lower:
            complaint_pattern['final_responses'].append(email)
            
        if 'complaint' in subject_lower:
            complaint_pattern['total_complaints'] += 1
    
    return complaint_pattern

def main():
    # Read emails
    csv_path = Path('email_analysis/email_summary.csv')
    
    # Storage for detailed findings
    treatment_evidence = {
        'purchase_journey': [],
        'communication_failures': [],
        'broken_promises': [],
        'delays': [],
        'poor_responses': [],
        'key_events': []
    }
    
    # Read all emails
    all_emails = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = parse_date(row['date'])
            if date and date >= datetime(2023, 1, 1, tzinfo=date.tzinfo):
                if '25 abbots' not in row['subject'].lower():
                    all_emails.append(row)
    
    # Sort by date
    all_emails.sort(key=lambda x: x['date'])
    
    # Key milestones to track
    milestones = {
        'reservation': None,
        'completion': None,
        'first_complaint': None,
        'settlement': None
    }
    
    # Analyze emails
    for i, email in enumerate(all_emails):
        subject_lower = email['subject'].lower()
        
        # Track milestones
        if 'reservation' in subject_lower and not milestones['reservation']:
            milestones['reservation'] = email
            treatment_evidence['key_events'].append({
                'date': email['date'],
                'event': 'Property reserved',
                'details': email['subject']
            })
            
        if 'completion' in subject_lower and not milestones['completion']:
            milestones['completion'] = email
            treatment_evidence['key_events'].append({
                'date': email['date'],
                'event': 'Property completed',
                'details': email['subject']
            })
            
        if 'complaint' in subject_lower and not milestones['first_complaint']:
            milestones['first_complaint'] = email
            treatment_evidence['key_events'].append({
                'date': email['date'],
                'event': 'First formal complaint',
                'details': email['subject']
            })
            
        if 'settlement' in subject_lower and not milestones['settlement']:
            milestones['settlement'] = email
            treatment_evidence['key_events'].append({
                'date': email['date'],
                'event': 'Settlement offered',
                'details': email['subject']
            })
        
        # Look for evidence of poor treatment
        if any(word in subject_lower for word in ['urgent', 'chase', 'reminder', 'awaiting']):
            treatment_evidence['communication_failures'].append({
                'date': email['date'],
                'subject': email['subject'],
                'from': email['from'],
                'evidence': 'Customer had to chase for response'
            })
            
        if any(word in subject_lower for word in ['delay', 'late', 'overdue']):
            treatment_evidence['delays'].append({
                'date': email['date'],
                'subject': email['subject'],
                'from': email['from'],
                'evidence': 'Delay in process or response'
            })
    
    # Analyze complaint handling
    complaint_emails = [e for e in all_emails if 'complaint' in e['subject'].lower()]
    complaint_pattern = analyze_complaint_pattern(complaint_emails)
    
    # Calculate complaint duration
    if milestones['first_complaint'] and len(complaint_emails) > 0:
        first_date = parse_date(milestones['first_complaint']['date'])
        last_date = parse_date(complaint_emails[-1]['date'])
        if first_date and last_date:
            complaint_duration = (last_date - first_date).days
            treatment_evidence['key_events'].append({
                'date': complaint_emails[-1]['date'],
                'event': 'Complaint still ongoing',
                'details': f'Complaint has been active for {complaint_duration} days'
            })
    
    # Output results
    output_dir = Path('nhos_complaint_analysis')
    
    # Save detailed treatment evidence
    treatment_file = output_dir / 'treatment_evidence.json'
    with open(treatment_file, 'w') as f:
        json.dump(treatment_evidence, f, indent=2)
    
    # Save complaint pattern analysis
    pattern_file = output_dir / 'complaint_pattern.json'
    with open(pattern_file, 'w') as f:
        # Convert email objects to serializable format
        pattern_data = {
            'total_complaints': complaint_pattern['total_complaints'],
            'acknowledgements_count': len(complaint_pattern['acknowledgements']),
            'pathways_count': len(complaint_pattern['pathways']),
            'assessments_count': len(complaint_pattern['assessments']),
            'interim_updates_count': len(complaint_pattern['interim_updates']),
            'final_responses_count': len(complaint_pattern['final_responses'])
        }
        json.dump(pattern_data, f, indent=2)
    
    # Create detailed report
    report_file = output_dir / 'detailed_treatment_report.md'
    with open(report_file, 'w') as f:
        f.write("# Detailed Analysis: Treatment During Plot 34 Purchase\n\n")
        
        f.write("## Key Timeline\n\n")
        for event in sorted(treatment_evidence['key_events'], key=lambda x: x['date']):
            date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
            f.write(f"- **{date.strftime('%Y-%m-%d')}**: {event['event']}\n")
            f.write(f"  - {event['details']}\n\n")
        
        f.write("## Complaint Handling Analysis\n\n")
        f.write(f"- Total complaint-related emails: {complaint_pattern['total_complaints']}\n")
        f.write(f"- Acknowledgements sent: {len(complaint_pattern['acknowledgements'])}\n")
        f.write(f"- Pathway to resolution letters: {len(complaint_pattern['pathways'])}\n")
        f.write(f"- Assessment & response letters: {len(complaint_pattern['assessments'])}\n")
        f.write(f"- Interim updates: {len(complaint_pattern['interim_updates'])}\n")
        f.write(f"- Final responses: {len(complaint_pattern['final_responses'])}\n\n")
        
        f.write("## Evidence of Poor Treatment\n\n")
        
        f.write("### Communication Failures\n")
        f.write(f"**{len(treatment_evidence['communication_failures'])} instances where customer had to chase**\n\n")
        for item in treatment_evidence['communication_failures'][:5]:
            date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
            f.write(f"- {date.strftime('%Y-%m-%d')}: {item['subject']}\n")
        
        f.write(f"\n### Delays\n")
        f.write(f"**{len(treatment_evidence['delays'])} instances of delays**\n\n")
        for item in treatment_evidence['delays'][:5]:
            date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
            f.write(f"- {date.strftime('%Y-%m-%d')}: {item['subject']}\n")
    
    print(f"\nDetailed treatment analysis complete!")
    print(f"Key events identified: {len(treatment_evidence['key_events'])}")
    print(f"Communication failures: {len(treatment_evidence['communication_failures'])}")
    print(f"Delays documented: {len(treatment_evidence['delays'])}")
    print(f"\nResults saved to {output_dir}/")

if __name__ == "__main__":
    main()