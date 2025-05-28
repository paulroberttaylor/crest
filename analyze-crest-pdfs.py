#!/usr/bin/env python3
"""
Analyze PDF content from Crest Nicholson emails.
This script attempts to extract text content from PDFs for analysis.
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

def analyze_pdf_metadata(pdf_dir):
    """Analyze PDFs based on filenames and create a summary."""
    
    pdf_files = sorted(Path(pdf_dir).glob('*.pdf'))
    
    analysis = {
        'total_pdfs': len(pdf_files),
        'categories': {},
        'timeline': [],
        'key_documents': []
    }
    
    for pdf_path in pdf_files:
        filename = pdf_path.name
        
        # Parse filename components
        parts = filename.split('_', 3)
        if len(parts) >= 4:
            date_str = parts[0]
            time_str = parts[1]
            subject = parts[2]
            original_name = parts[3].replace('.pdf', '')
            
            # Categorize by document type
            doc_type = 'other'
            if 'complaint' in filename.lower():
                doc_type = 'complaint_correspondence'
            elif 'settlement' in filename.lower():
                doc_type = 'settlement'
            elif 'reservation' in filename.lower() or 'res' in original_name.lower():
                doc_type = 'reservation'
            elif 'completion' in filename.lower():
                doc_type = 'completion'
            elif 'nhbc' in filename.lower():
                doc_type = 'warranty'
            elif 'snag' in filename.lower():
                doc_type = 'snag_list'
            elif 'choices' in filename.lower() or 'options' in filename.lower():
                doc_type = 'customer_choices'
            elif 'guide' in filename.lower() or 'brochure' in filename.lower():
                doc_type = 'information_guides'
            elif 'overlay' in filename.lower() or 'drawing' in filename.lower():
                doc_type = 'technical_drawings'
            
            if doc_type not in analysis['categories']:
                analysis['categories'][doc_type] = []
            
            doc_info = {
                'filename': filename,
                'date': date_str,
                'subject': subject,
                'original_name': original_name,
                'size': pdf_path.stat().st_size
            }
            
            analysis['categories'][doc_type].append(doc_info)
            analysis['timeline'].append(doc_info)
            
            # Identify key documents
            key_indicators = [
                'final response', 'settlement', 'completion', 'pathway to resolution',
                'assessment and response', 'acknowledgement'
            ]
            if any(indicator in filename.lower() for indicator in key_indicators):
                analysis['key_documents'].append(doc_info)
    
    # Sort timeline by date
    analysis['timeline'].sort(key=lambda x: x['date'])
    
    return analysis

def print_analysis(analysis):
    """Print a formatted analysis of the PDFs."""
    
    print(f"# Crest Nicholson PDF Analysis")
    print(f"\nTotal PDFs: {analysis['total_pdfs']}")
    
    print(f"\n## Document Categories:")
    for category, docs in analysis['categories'].items():
        print(f"\n### {category.replace('_', ' ').title()} ({len(docs)} documents)")
        for doc in sorted(docs, key=lambda x: x['date']):
            print(f"- {doc['date']} - {doc['original_name'][:80]}...")
    
    print(f"\n## Key Documents:")
    for doc in analysis['key_documents']:
        print(f"- **{doc['date']}** - {doc['original_name']}")
    
    print(f"\n## Chronological Summary:")
    
    # Group by year and month
    current_year = None
    current_month = None
    
    for doc in analysis['timeline']:
        try:
            date = datetime.strptime(doc['date'], '%Y-%m-%d')
            year = date.year
            month = date.strftime('%B')
            
            if year != current_year:
                print(f"\n### {year}")
                current_year = year
                current_month = None
            
            if month != current_month:
                print(f"\n**{month}**")
                current_month = month
            
            # Determine document description
            if 'complaint' in doc['original_name'].lower():
                if 'acknowledgement' in doc['original_name'].lower():
                    desc = "Complaint Acknowledgement"
                elif 'pathway' in doc['original_name'].lower():
                    desc = "Complaint Pathway to Resolution"
                elif 'assessment' in doc['original_name'].lower():
                    desc = "Complaint Assessment and Response"
                elif 'interim' in doc['original_name'].lower():
                    desc = "Complaint Interim Update"
                elif 'final' in doc['original_name'].lower():
                    desc = "Complaint Final Response"
                else:
                    desc = "Complaint Correspondence"
            elif 'settlement' in doc['original_name'].lower():
                desc = "Settlement Document"
            elif 'reservation' in doc['original_name'].lower():
                desc = "Reservation Agreement"
            elif 'completion' in doc['original_name'].lower():
                desc = "Completion Document"
            else:
                desc = doc['original_name'][:50]
            
            print(f"- {date.day}: {desc}")
            
        except:
            print(f"- {doc['date']}: {doc['original_name'][:60]}")
    
    # Save analysis to JSON
    output_file = 'pdf_attachments/crest_pdf_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\n\nDetailed analysis saved to: {output_file}")

def main():
    pdf_dir = 'pdf_attachments/crestnicholson.com'
    
    if not os.path.exists(pdf_dir):
        print(f"Error: Directory '{pdf_dir}' not found")
        sys.exit(1)
    
    print(f"Analyzing PDFs in: {pdf_dir}\n")
    
    analysis = analyze_pdf_metadata(pdf_dir)
    print_analysis(analysis)

if __name__ == "__main__":
    main()