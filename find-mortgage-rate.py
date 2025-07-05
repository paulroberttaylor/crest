#!/usr/bin/env python3
import mailbox
import email
from email.utils import parsedate_to_datetime

def find_mortgage_rate_emails(mbox_path):
    """Find emails mentioning mortgage rates, especially 1.5%"""
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
            
            # Check if this involves mortgage workshop or Leanne
            all_addrs = f"{from_addr} {to_addr} {cc_addr}"
            if 'mortgageworkshop' not in all_addrs and 'leanne' not in all_addrs:
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
            
            # Look for rate mentions
            if '1.5' in body or 'rate' in body.lower() or 'mortgage' in body.lower():
                found_count += 1
                print("="*80)
                print(f"EMAIL #{found_count}")
                print(f"Date: {date_str}")
                print(f"From: {message.get('From', '')}")
                print(f"To: {message.get('To', '')}")
                print(f"Subject: {subject}")
                print("\nRelevant content:")
                
                # Print lines containing rates or mortgage info
                for line in body.split('\n'):
                    line_lower = line.lower()
                    if ('1.5' in line or 'rate' in line_lower or 'mortgage' in line_lower or 
                        'percent' in line_lower or '%' in line):
                        print(f"  >>> {line.strip()}")
                
                print("\n")
                
        except Exception as e:
            continue
    
    print(f"\nTotal emails found: {found_count}")

if __name__ == "__main__":
    find_mortgage_rate_emails("Crest-NHOS-Export-001.mbox")