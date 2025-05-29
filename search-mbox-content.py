#!/usr/bin/env python3
"""
Search MBOX file for specific content in email bodies.
This searches the actual email content, not just headers.
"""

import mailbox
import email
from email.utils import parsedate_to_datetime
import sys
import re
from datetime import datetime

def search_email_body(msg, search_terms):
    """Search email body for terms."""
    try:
        # Get the email body
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
                elif part.get_content_type() == "text/html":
                    try:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Simple HTML tag removal
                        body += re.sub('<[^<]+?>', '', html_body)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        # Search for terms
        body_lower = body.lower()
        for term in search_terms:
            if term.lower() in body_lower:
                return True, body
                
        return False, body
        
    except Exception as e:
        return False, ""

def extract_context(body, search_terms, context_size=200):
    """Extract context around search terms."""
    body_lower = body.lower()
    contexts = []
    
    for term in search_terms:
        term_lower = term.lower()
        index = body_lower.find(term_lower)
        while index != -1:
            start = max(0, index - context_size)
            end = min(len(body), index + len(term) + context_size)
            context = body[start:end]
            
            # Clean up context
            context = ' '.join(context.split())
            if start > 0:
                context = "..." + context
            if end < len(body):
                context = context + "..."
            
            contexts.append((term, context))
            
            # Find next occurrence
            index = body_lower.find(term_lower, index + 1)
    
    return contexts

def search_mbox(mbox_path, search_terms, date_from=None, date_to=None):
    """Search MBOX for specific terms in email bodies."""
    
    print(f"Searching for: {', '.join(search_terms)}")
    if date_from:
        print(f"From date: {date_from}")
    print()
    
    mbox = mailbox.mbox(mbox_path)
    results = []
    total_searched = 0
    
    for key, msg in mbox.iteritems():
        total_searched += 1
        
        # Check date range
        if date_from:
            try:
                msg_date = parsedate_to_datetime(msg['Date'])
                if msg_date.replace(tzinfo=None) < date_from:
                    continue
                if date_to and msg_date.replace(tzinfo=None) > date_to:
                    continue
            except:
                continue
        
        # Search body
        found, body = search_email_body(msg, search_terms)
        
        if found:
            result = {
                'date': msg.get('Date', 'No date'),
                'from': msg.get('From', 'No sender'),
                'to': msg.get('To', 'No recipient'),
                'subject': msg.get('Subject', 'No subject'),
                'contexts': extract_context(body, search_terms)
            }
            results.append(result)
            
            # Print as we find them
            print(f"\n{'='*80}")
            print(f"Date: {result['date']}")
            print(f"From: {result['from']}")
            print(f"To: {result['to']}")
            print(f"Subject: {result['subject']}")
            print(f"\nMatching content:")
            for term, context in result['contexts'][:3]:  # Show first 3 contexts
                print(f"\n[{term}]: {context}")
            
            if len(result['contexts']) > 3:
                print(f"\n... and {len(result['contexts']) - 3} more matches")
    
    mbox.close()
    
    print(f"\n{'='*80}")
    print(f"\nSearch complete!")
    print(f"Total emails searched: {total_searched}")
    print(f"Emails with matches: {len(results)}")
    
    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python search-mbox-content.py <mbox_file> <search_term1> [search_term2] ...")
        print("\nExamples:")
        print('  python search-mbox-content.py file.mbox "air brick"')
        print('  python search-mbox-content.py file.mbox "air brick" "airbrick" "ventilation"')
        print('  python search-mbox-content.py file.mbox "buried" "drive" "driveway"')
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    search_terms = sys.argv[2:]
    
    # Set date range (optional)
    date_from = datetime(2023, 1, 1)  # Only search from Jan 2023
    
    results = search_mbox(mbox_path, search_terms, date_from)
    
    # Save results
    if results:
        output_file = f"mbox_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Search terms: {', '.join(search_terms)}\n")
            f.write(f"Date range: From {date_from}\n")
            f.write(f"Total matches: {len(results)}\n\n")
            
            for result in results:
                f.write(f"\n{'='*80}\n")
                f.write(f"Date: {result['date']}\n")
                f.write(f"From: {result['from']}\n")
                f.write(f"To: {result['to']}\n")
                f.write(f"Subject: {result['subject']}\n")
                f.write(f"\nMatching content:\n")
                for term, context in result['contexts']:
                    f.write(f"\n[{term}]: {context}\n")
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()