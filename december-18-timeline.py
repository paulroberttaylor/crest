#!/usr/bin/env python3
"""
Create detailed timeline of December 18, 2023 completion day
"""

import csv
from datetime import datetime

def analyze_completion_day():
    """Analyze emails from December 15-18, 2023."""
    
    completion_emails = []
    
    # Read the CSV
    with open('email_analysis/email_summary.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row.get('Date', '')
            if '2023-12-1' in date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if 15 <= dt.day <= 18:
                        completion_emails.append({
                            'datetime': dt,
                            'subject': row.get('Subject', ''),
                            'from': row.get('From', ''),
                            'to': row.get('To', ''),
                            'cc': row.get('CC', '')
                        })
                except:
                    pass
    
    # Sort by time
    completion_emails.sort(key=lambda x: x['datetime'])
    
    print("DECEMBER 15-18, 2023: COMPLETION CHAOS TIMELINE")
    print("=" * 80)
    
    current_day = None
    
    for email in completion_emails:
        dt = email['datetime']
        day = dt.strftime('%Y-%m-%d')
        
        if day != current_day:
            current_day = day
            print(f"\n\n{dt.strftime('%A, December %d, 2023')}")
            print("-" * 50)
        
        time_str = dt.strftime('%H:%M')
        from_person = email['from'].split('<')[0].strip()
        
        # Identify key people
        if 'paulroberttaylor' in email['from']:
            from_person = "Paul Taylor"
        elif 'jade.millington' in email['from']:
            from_person = "Jade Taylor"
        elif 'Hannah Rafferty' in from_person or 'hr@bramsdon' in email['from']:
            from_person = "Hannah Rafferty (Solicitor)"
        elif 'Eileen.Guihen' in email['from']:
            from_person = "Eileen Guihen (Crest Deputy MD)"
        elif 'Steve.Smith' in email['from']:
            from_person = "Steve Smith (Crest)"
        elif 'Lynn.Carrington' in email['from']:
            from_person = "Lynn Carrington (Crest)"
        elif 'Natalie.Haigh' in email['from']:
            from_person = "Natalie Haigh (Crest)"
        elif 'Maja.Janusz' in email['from']:
            from_person = "Maja Janusz (Crest Solicitor)"
        elif 'Leanna.Hill' in email['from'] or 'lh@bramsdon' in email['from']:
            from_person = "Leanna Hill (B&C)"
        
        print(f"\n{time_str} - {from_person}")
        print(f"Subject: {email['subject']}")
        
        # Show recipients
        to_list = []
        for addr in email['to'].split(','):
            if 'paulroberttaylor' in addr:
                to_list.append("Paul")
            elif 'jade' in addr:
                to_list.append("Jade")
            elif 'Hannah' in addr or 'hr@bramsdon' in addr:
                to_list.append("Hannah Rafferty")
            elif 'Eileen' in addr:
                to_list.append("Eileen Guihen")
            elif 'Steve' in addr:
                to_list.append("Steve Smith")
            elif 'Lynn' in addr:
                to_list.append("Lynn Carrington")
            elif '@crestnicholson' in addr:
                to_list.append("Crest")
            elif '@bramsdon' in addr:
                to_list.append("B&C")
        
        if to_list:
            print(f"To: {', '.join(to_list)}")
    
    # Add analysis
    print("\n\n" + "=" * 80)
    print("KEY OBSERVATIONS:")
    print("=" * 80)
    
    print("\nDECEMBER 18, 2023 - COMPLETION DAY CHAOS:")
    print("- 13:50 - Paul contacts Steve Smith at Crest (starting the day)")
    print("- 14:23 - Steve tells Paul they'll let him know about key release")
    print("- 14:24 - Paul escalates to Eileen Guihen (Deputy MD)")
    print("- 14:28 - Eileen says NO KEYS until legal completion")
    print("- 14:31 - Compromise: Paul can unload in garage only")
    print("- 14:54 - Eileen reiterates: 'Keys are never released prior to legal completion'")
    print("- 16:27 - FINALLY: 'Funds released... Key release instructed'")
    print("\nPaul and Jade spent OVER 2 HOURS on completion day waiting for keys!")
    print("Contract/legal issues were STILL not resolved even on the day of completion.")

if __name__ == "__main__":
    analyze_completion_day()