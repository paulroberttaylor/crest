#!/usr/bin/env python3
"""
Search for specific issues in the email database:
1. DPC (damp proof course) issues at the rear of the garage
2. Air brick or airbrick being buried or half buried
3. Gutters with debris - specifically any email from Natalie Haigh denying this
4. Build manager or site manager claiming to have checked the house 15 times
"""

import chromadb
from chromadb.config import Settings
import json
from datetime import datetime
import re

def search_emails(collection, query, n_results=20):
    """Search emails and return results"""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    
    return results

def extract_relevant_content(email_text, search_terms):
    """Extract sentences containing search terms"""
    lines = email_text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for term in search_terms:
            if term.lower() in line_lower:
                # Get context (line before and after)
                start = max(0, i-1)
                end = min(len(lines), i+2)
                context = '\n'.join(lines[start:end])
                relevant_lines.append(context)
                break
    
    return '\n---\n'.join(relevant_lines)

def main():
    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path="chromadb_emails_quick",
        settings=Settings(anonymized_telemetry=False)
    )
    
    collection = client.get_collection("emails_quick")
    
    # Search topics
    searches = [
        {
            "query": "DPC damp proof course garage rear",
            "terms": ["dpc", "damp proof course", "garage", "rear"],
            "description": "DPC issues at rear of garage"
        },
        {
            "query": "air brick airbrick buried half covered",
            "terms": ["air brick", "airbrick", "buried", "half", "covered"],
            "description": "Air brick buried or half buried"
        },
        {
            "query": "gutters debris Natalie Haigh deny denied",
            "terms": ["gutter", "debris", "natalie haigh", "deny", "denied", "no debris"],
            "description": "Gutters with debris - Natalie Haigh denial"
        },
        {
            "query": "build manager site manager checked 15 times fifteen",
            "terms": ["build manager", "site manager", "checked", "15 times", "fifteen", "15"],
            "description": "Build/site manager claiming 15 checks"
        }
    ]
    
    # Results storage
    all_findings = []
    
    for search in searches:
        print(f"\n{'='*80}")
        print(f"Searching for: {search['description']}")
        print(f"Query: {search['query']}")
        print("="*80)
        
        results = search_emails(collection, search['query'], n_results=30)
        
        findings = []
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            # Filter by date (2023-2024)
            date_str = metadata.get('date', '')
            if date_str:
                try:
                    email_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                    if email_date.year < 2023 or email_date.year > 2024:
                        continue
                except:
                    pass
            
            # Extract relevant content
            relevant_content = extract_relevant_content(doc, search['terms'])
            
            if relevant_content:
                finding = {
                    'date': metadata.get('date', 'Unknown'),
                    'from': metadata.get('from', 'Unknown'),
                    'to': metadata.get('to', 'Unknown'),
                    'subject': metadata.get('subject', 'No subject'),
                    'relevance_score': 1 - distance,
                    'relevant_content': relevant_content,
                    'full_content': doc[:1000] + '...' if len(doc) > 1000 else doc
                }
                findings.append(finding)
                
                print(f"\n--- Email {i+1} ---")
                print(f"Date: {finding['date']}")
                print(f"From: {finding['from']}")
                print(f"To: {finding['to']}")
                print(f"Subject: {finding['subject']}")
                print(f"Relevance: {finding['relevance_score']:.2f}")
                print(f"\nRelevant Content:")
                print(finding['relevant_content'][:500] + '...' if len(finding['relevant_content']) > 500 else finding['relevant_content'])
        
        all_findings.append({
            'search': search['description'],
            'query': search['query'],
            'findings': findings
        })
        
        print(f"\nFound {len(findings)} relevant emails for this search")
    
    # Save results
    with open('specific_issues_search_results.json', 'w') as f:
        json.dump(all_findings, f, indent=2)
    
    print(f"\n\nResults saved to specific_issues_search_results.json")
    
    # Generate summary report
    with open('specific_issues_report.md', 'w') as f:
        f.write("# Specific Issues Search Report\n\n")
        f.write("Search Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        
        for search_result in all_findings:
            f.write(f"\n## {search_result['search']}\n\n")
            f.write(f"**Query:** {search_result['query']}\n\n")
            f.write(f"**Found:** {len(search_result['findings'])} relevant emails\n\n")
            
            for finding in search_result['findings']:
                f.write(f"\n### Email: {finding['date']} - {finding['subject']}\n")
                f.write(f"- **From:** {finding['from']}\n")
                f.write(f"- **To:** {finding['to']}\n")
                f.write(f"- **Relevance Score:** {finding['relevance_score']:.2f}\n\n")
                f.write("**Relevant Content:**\n```\n")
                f.write(finding['relevant_content'])
                f.write("\n```\n\n")
                f.write("---\n")
    
    print("Summary report saved to specific_issues_report.md")

if __name__ == "__main__":
    main()