#!/usr/bin/env python3
"""
Extract PDF attachments from MBOX file and save them with meaningful names.
"""

import mailbox
import email
from email.utils import parsedate_to_datetime, getaddresses
import os
import sys
from pathlib import Path
import json
import re

def sanitize_filename(filename):
    """Clean filename for filesystem compatibility."""
    # Remove/replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    return filename

def get_sender_domain(msg):
    """Extract sender's domain from email."""
    from_field = msg.get('From', '')
    addresses = getaddresses([from_field])
    if addresses and addresses[0][1]:
        email_addr = addresses[0][1].lower()
        if '@' in email_addr:
            return email_addr.split('@')[1]
    return 'unknown'

def extract_pdfs_from_mbox(mbox_path, output_dir):
    """Extract all PDF attachments from MBOX file."""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create subdirectories for each domain
    domains = ['crestnicholson.com', 'nhos.org.uk', 'bramsdonandchilds.com', 'other']
    for domain in domains:
        (output_path / domain).mkdir(exist_ok=True)
    
    # Track extracted PDFs
    pdf_inventory = []
    
    print(f"Opening {mbox_path}...")
    mbox = mailbox.mbox(mbox_path)
    
    total_emails = 0
    pdfs_extracted = 0
    
    for key, msg in mbox.iteritems():
        total_emails += 1
        
        # Get email metadata
        date = msg.get('Date', '')
        subject = msg.get('Subject', 'No Subject')
        sender_domain = get_sender_domain(msg)
        
        # Parse date
        try:
            dt = parsedate_to_datetime(date)
            date_str = dt.strftime('%Y-%m-%d_%H%M')
        except:
            date_str = 'unknown_date'
        
        # Check for attachments
        for part in msg.walk():
            if part.get_content_type() == 'application/pdf':
                filename = part.get_filename()
                if filename:
                    # Get PDF content
                    pdf_content = part.get_payload(decode=True)
                    
                    # Determine output directory based on sender domain
                    if 'crestnicholson.com' in sender_domain:
                        domain_dir = 'crestnicholson.com'
                    elif 'nhos.org.uk' in sender_domain:
                        domain_dir = 'nhos.org.uk'
                    elif 'bramsdonandchilds.com' in sender_domain:
                        domain_dir = 'bramsdonandchilds.com'
                    else:
                        domain_dir = 'other'
                    
                    # Create descriptive filename
                    clean_subject = sanitize_filename(subject)[:50]
                    clean_filename = sanitize_filename(filename)
                    new_filename = f"{date_str}_{clean_subject}_{clean_filename}"
                    
                    # Ensure unique filename
                    output_file = output_path / domain_dir / new_filename
                    counter = 1
                    while output_file.exists():
                        name, ext = os.path.splitext(new_filename)
                        output_file = output_path / domain_dir / f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # Save PDF
                    with open(output_file, 'wb') as f:
                        f.write(pdf_content)
                    
                    pdfs_extracted += 1
                    
                    # Add to inventory
                    pdf_inventory.append({
                        'filename': str(output_file.name),
                        'path': str(output_file),
                        'original_filename': filename,
                        'email_subject': subject,
                        'email_date': date,
                        'sender_domain': sender_domain,
                        'size_bytes': len(pdf_content)
                    })
                    
                    print(f"Extracted: {output_file.name}")
        
        if total_emails % 100 == 0:
            print(f"Processed {total_emails} emails...")
    
    # Save inventory
    inventory_file = output_path / 'pdf_inventory.json'
    with open(inventory_file, 'w') as f:
        json.dump(pdf_inventory, f, indent=2)
    
    # Create summary
    summary_file = output_path / 'pdf_summary.md'
    with open(summary_file, 'w') as f:
        f.write("# PDF Attachments Summary\n\n")
        f.write(f"Total emails processed: {total_emails}\n")
        f.write(f"Total PDFs extracted: {pdfs_extracted}\n\n")
        
        # Group by domain
        for domain in domains:
            domain_pdfs = [p for p in pdf_inventory if domain in p['sender_domain'] or (domain == 'other' and not any(d in p['sender_domain'] for d in domains[:3]))]
            if domain_pdfs:
                f.write(f"\n## {domain} ({len(domain_pdfs)} PDFs)\n\n")
                for pdf in sorted(domain_pdfs, key=lambda x: x['email_date']):
                    f.write(f"- **{pdf['email_date'][:10]}** - {pdf['email_subject']}\n")
                    f.write(f"  - File: {pdf['filename']}\n")
                    f.write(f"  - Size: {pdf['size_bytes']:,} bytes\n")
    
    mbox.close()
    
    print(f"\nExtraction complete!")
    print(f"Total PDFs extracted: {pdfs_extracted}")
    print(f"PDFs saved to: {output_path}")
    print(f"Inventory saved to: {inventory_file}")
    print(f"Summary saved to: {summary_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract-pdf-attachments.py <mbox_file>")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    
    if not os.path.exists(mbox_path):
        print(f"Error: File '{mbox_path}' not found")
        sys.exit(1)
    
    output_dir = "pdf_attachments"
    extract_pdfs_from_mbox(mbox_path, output_dir)

if __name__ == "__main__":
    main()