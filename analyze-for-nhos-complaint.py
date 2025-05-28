#!/usr/bin/env python3
"""
Analyze emails from January 1, 2023 onwards to build NHOS complaint evidence.
Categories based on New Homes Quality Code violations.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
import sys

# NHOS Code violation categories based on the Quality Code
COMPLAINT_CATEGORIES = {
    'fairness': 'Part 1.1-1.3: Fairness - misleading information, high-pressure sales',
    'transparency': 'Part 1.2: Transparency - incomplete/misleading property descriptions', 
    'customer_service': 'Part 1.6: Customer service standards and training',
    'reservation': 'Part 2.2-2.5: Reservation agreement issues',
    'pre_contract': 'Part 2.6: Pre-contract information not provided',
    'keeping_informed': 'Part 2.8: Failure to keep customer informed',
    'changes': 'Part 2.9: Changes without proper notification',
    'completion': 'Part 2.10-2.11: Completion issues',
    'after_sales': 'Part 3.1-3.2: After-sales service failures',
    'complaints_process': 'Part 3.4: Complaints process violations',
    'defects': 'Part 3.3: Defects and snagging issues',
    'responsiveness': 'Principle 5: Lack of responsiveness',
    'quality': 'Principle 3: Quality issues'
}

def parse_date(date_str):
    """Parse ISO date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None

def analyze_email_content(subject, sender, recipient, date):
    """Analyze email and categorize for NHOS complaint."""
    subject_lower = subject.lower()
    findings = []
    
    # Keywords for categorization
    if any(word in subject_lower for word in ['complaint', 'pathway', 'resolution', 'assessment', 'response']):
        findings.append({
            'category': 'complaints_process',
            'evidence': f"Complaint correspondence: {subject}",
            'date': date
        })
    
    if any(word in subject_lower for word in ['render', 'crack', 'defect', 'snag', 'issue', 'problem']):
        findings.append({
            'category': 'defects',
            'evidence': f"Defect/quality issue: {subject}",
            'date': date
        })
    
    if any(word in subject_lower for word in ['path', 'cycle', 'link', 'bridal', 'bridleway', 'access']):
        findings.append({
            'category': 'changes',
            'evidence': f"Path/development connection issue: {subject}",
            'date': date
        })
    
    if any(word in subject_lower for word in ['settlement', 'offer']):
        findings.append({
            'category': 'after_sales',
            'evidence': f"Settlement discussion: {subject}",
            'date': date
        })
    
    if any(word in subject_lower for word in ['reservation', 'contract', 'legal', 'completion']):
        findings.append({
            'category': 'reservation',
            'evidence': f"Purchase process: {subject}",
            'date': date
        })
    
    if any(word in subject_lower for word in ['delay', 'waiting', 'chase', 'urgent', 'reminder']):
        findings.append({
            'category': 'responsiveness',
            'evidence': f"Responsiveness issue: {subject}",
            'date': date
        })
    
    if any(word in subject_lower for word in ['nhbc', 'warranty', 'certificate']):
        findings.append({
            'category': 'completion',
            'evidence': f"Warranty/certification: {subject}",
            'date': date
        })
    
    return findings

def main():
    # Read the email summary CSV
    csv_path = Path('email_analysis/email_summary.csv')
    if not csv_path.exists():
        print(f"Error: {csv_path} not found. Run mbox-analyzer.py first.")
        sys.exit(1)
    
    # Date cutoff
    cutoff_date = datetime(2023, 1, 1, tzinfo=datetime.now().astimezone().tzinfo)
    
    # Storage for findings
    complaint_evidence = {cat: [] for cat in COMPLAINT_CATEGORIES}
    timeline = []
    summary_stats = {
        'total_emails': 0,
        'relevant_emails': 0,
        'complaint_emails': 0,
        'render_emails': 0,
        'path_emails': 0,
        'violations_by_category': {}
    }
    
    # Process emails
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            email_date = parse_date(row['date'])
            if not email_date or email_date < cutoff_date:
                continue
            
            summary_stats['total_emails'] += 1
            
            # Skip if about 25 Abbots Road
            if '25 abbots' in row['subject'].lower():
                continue
            
            # Analyze email
            findings = analyze_email_content(
                row['subject'],
                row['from'],
                row['to'],
                row['date']
            )
            
            if findings:
                summary_stats['relevant_emails'] += 1
                
                # Track specific issues
                subject_lower = row['subject'].lower()
                if 'complaint' in subject_lower:
                    summary_stats['complaint_emails'] += 1
                if 'render' in subject_lower:
                    summary_stats['render_emails'] += 1
                if any(word in subject_lower for word in ['path', 'cycle', 'bridal']):
                    summary_stats['path_emails'] += 1
                
                # Add to timeline
                timeline_entry = {
                    'date': row['date'],
                    'subject': row['subject'],
                    'from': row['from'],
                    'to': row['to'],
                    'categories': [f['category'] for f in findings]
                }
                timeline.append(timeline_entry)
                
                # Categorize findings
                for finding in findings:
                    complaint_evidence[finding['category']].append({
                        'date': row['date'],
                        'subject': row['subject'],
                        'from': row['from'],
                        'to': row['to'],
                        'evidence': finding['evidence']
                    })
    
    # Count violations by category
    for cat, items in complaint_evidence.items():
        if items:
            summary_stats['violations_by_category'][cat] = len(items)
    
    # Sort timeline
    timeline.sort(key=lambda x: x['date'])
    
    # Output results
    output_dir = Path('nhos_complaint_analysis')
    output_dir.mkdir(exist_ok=True)
    
    # Save detailed evidence by category
    evidence_file = output_dir / 'complaint_evidence_by_category.json'
    with open(evidence_file, 'w') as f:
        json.dump(complaint_evidence, f, indent=2)
    
    # Save timeline
    timeline_file = output_dir / 'complaint_timeline.json'
    with open(timeline_file, 'w') as f:
        json.dump(timeline, f, indent=2)
    
    # Save summary statistics
    stats_file = output_dir / 'complaint_statistics.json'
    with open(stats_file, 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    # Create markdown report
    report_file = output_dir / 'nhos_complaint_report.md'
    with open(report_file, 'w') as f:
        f.write("# NHOS Complaint Evidence Analysis\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        f.write("## Summary Statistics\n\n")
        f.write(f"- Total emails analyzed (from Jan 1, 2023): {summary_stats['total_emails']}\n")
        f.write(f"- Emails with complaint evidence: {summary_stats['relevant_emails']}\n")
        f.write(f"- Formal complaint emails: {summary_stats['complaint_emails']}\n")
        f.write(f"- Render issue emails: {summary_stats['render_emails']}\n")
        f.write(f"- Path/cycle link emails: {summary_stats['path_emails']}\n\n")
        
        f.write("## Code Violations by Category\n\n")
        for cat, count in sorted(summary_stats['violations_by_category'].items(), 
                                key=lambda x: x[1], reverse=True):
            f.write(f"- **{COMPLAINT_CATEGORIES[cat]}**: {count} instances\n")
        
        f.write("\n## Detailed Evidence by Category\n\n")
        for cat, items in complaint_evidence.items():
            if items:
                f.write(f"### {COMPLAINT_CATEGORIES[cat]}\n\n")
                f.write(f"**{len(items)} instances found**\n\n")
                
                # Show first 5 examples
                for i, item in enumerate(items[:5]):
                    date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    f.write(f"{i+1}. **{date.strftime('%Y-%m-%d')}** - {item['subject']}\n")
                    f.write(f"   - From: {item['from']}\n")
                    f.write(f"   - Evidence: {item['evidence']}\n\n")
                
                if len(items) > 5:
                    f.write(f"... and {len(items) - 5} more instances\n\n")
        
        f.write("\n## Key Timeline Events\n\n")
        
        # Group by month
        current_month = None
        for entry in timeline:
            date = datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
            month_key = date.strftime('%Y-%m')
            
            if month_key != current_month:
                current_month = month_key
                f.write(f"\n### {date.strftime('%B %Y')}\n\n")
            
            f.write(f"- **{date.strftime('%d')}**: {entry['subject']}\n")
            if len(entry['categories']) > 1:
                f.write(f"  - Categories: {', '.join(entry['categories'])}\n")
    
    print(f"\nAnalysis complete!")
    print(f"Total emails from 2023 onwards: {summary_stats['total_emails']}")
    print(f"Emails with complaint evidence: {summary_stats['relevant_emails']}")
    print(f"\nResults saved to {output_dir}/")
    print(f"- Detailed evidence: complaint_evidence_by_category.json")
    print(f"- Timeline: complaint_timeline.json") 
    print(f"- Statistics: complaint_statistics.json")
    print(f"- Report: nhos_complaint_report.md")

if __name__ == "__main__":
    main()