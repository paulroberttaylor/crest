#!/usr/bin/env python3
import mailbox
import email
import os
import base64
from datetime import datetime

def extract_pdfs_from_mortgage_emails(mbox_path, output_dir="mortgage_pdfs"):
    """Extract PDFs from mortgage workshop emails"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    mbox = mailbox.mbox(mbox_path)
    pdf_count = 0
    
    for i, message in enumerate(mbox):
        try:
            from_addr = message.get('From', '').lower()
            to_addr = message.get('To', '').lower()
            cc_addr = message.get('Cc', '').lower()
            date_str = message.get('Date', '')
            subject = message.get('Subject', 'No Subject')
            
            # Check if this involves mortgage workshop or Leanne
            all_addrs = f"{from_addr} {to_addr} {cc_addr}"
            if 'mortgageworkshop' not in all_addrs and 'leanne' not in all_addrs:
                continue
            
            # Look for PDF attachments
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == 'application/pdf':
                        filename = part.get_filename()
                        if filename:
                            pdf_count += 1
                            # Clean filename
                            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
                            safe_filename = f"{pdf_count:03d}_{safe_filename}"
                            
                            # Get PDF content
                            pdf_content = part.get_payload(decode=True)
                            
                            # Save PDF
                            pdf_path = os.path.join(output_dir, safe_filename)
                            with open(pdf_path, 'wb') as f:
                                f.write(pdf_content)
                            
                            print(f"Extracted: {safe_filename}")
                            print(f"  From: {message.get('From', '')}")
                            print(f"  Date: {date_str}")
                            print(f"  Subject: {subject}")
                            print()
                            
        except Exception as e:
            print(f"Error processing message {i}: {e}")
            continue
    
    print(f"\nTotal PDFs extracted: {pdf_count}")
    return pdf_count

if __name__ == "__main__":
    extract_pdfs_from_mortgage_emails("Crest-NHOS-Export-001.mbox")