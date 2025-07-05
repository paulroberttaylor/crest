#!/usr/bin/env python3
import mailbox
import email
from email.utils import parsedate_to_datetime
import re

def extract_mortgage_rate_info(mbox_path):
    """Find emails with specific mortgage rate mentions"""
    mbox = mailbox.mbox(mbox_path)
    found_count = 0
    
    for message in mbox:
        try:
            # Get email details
            from_addr = message.get('From', '').lower()
            to_addr = message.get('To', '').lower()
            cc_addr = message.get('Cc', '').lower()
            subject = message.get('Subject', '')
            date_str = message.get('Date', '')
            
            # Parse date to check if it's from 2023
            try:
                date_obj = parsedate_to_datetime(date_str)
                if not (date_obj.year == 2023 and date_obj.month <= 6):
                    continue
            except:
                continue
            
            # Get body
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                        except:
                            pass
            else:
                try:
                    body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = str(message.get_payload())
            
            # Look for specific rate patterns (e.g., 1.5%, 2.0%, 3.64%, etc.)
            rate_patterns = [
                r'\b\d+\.\d+\s*%',  # Matches patterns like "1.5 %" or "3.64%"
                r'\b\d+\.\d+\s+fixed',  # Matches patterns like "3.64 fixed"
                r'rate.*\d+\.\d+',  # Matches "rate" followed by a number
                r'mortgage.*\d+\.\d+',  # Matches "mortgage" followed by a number
            ]
            
            found_rates = []
            for pattern in rate_patterns:
                matches = re.findall(pattern, body, re.IGNORECASE)
                found_rates.extend(matches)
            
            if found_rates and ('mortgage' in body.lower() or 'leanne' in from_addr or 'leanne' in to_addr):
                found_count += 1
                print("="*80)
                print(f"EMAIL #{found_count}")
                print(f"Date: {date_str}")
                print(f"From: {message.get('From', '')}")
                print(f"To: {message.get('To', '')}")
                print(f"Subject: {subject}")
                print(f"\nFound rates: {', '.join(set(found_rates))}")
                print("\nRelevant excerpts:")
                
                # Print lines containing rates
                for line in body.split('\n'):
                    if any(rate in line for rate in found_rates):
                        print(f"  >>> {line.strip()}")
                
                # Also look for mortgage offer mentions
                for line in body.split('\n'):
                    line_lower = line.lower()
                    if ('offer' in line_lower or 'dip' in line_lower or 'decision' in line_lower or
                        'mortgage illustration' in line_lower):
                        print(f"  >>> {line.strip()}")
                
                print("\n")
                
        except Exception as e:
            continue
    
    print(f"\nTotal emails with mortgage rates found: {found_count}")

if __name__ == "__main__":
    extract_mortgage_rate_info("Crest-NHOS-Export-001.mbox")