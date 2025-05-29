#!/usr/bin/env python3
"""
ChromaDB Email Indexer with PDF Extraction
Indexes all emails and PDF attachments in a searchable vector database
"""

import mailbox
import email
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import json
import os
import sys
import re
import hashlib
from typing import Dict, List, Optional, Tuple
import chromadb
from chromadb.utils import embedding_functions
import pdfplumber
from PyPDF2 import PdfReader
import warnings
warnings.filterwarnings("ignore")

class EmailIndexer:
    def __init__(self, mbox_path: str, pdf_dir: str = "pdf_attachments"):
        self.mbox_path = mbox_path
        self.pdf_dir = pdf_dir
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails")
        
        # Use the default embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create or get collection
        try:
            self.collection = self.client.create_collection(
                name="crest_emails",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        except:
            # Collection already exists
            self.client.delete_collection("crest_emails")
            self.collection = self.client.create_collection(
                name="crest_emails",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        
        self.processed_count = 0
        self.pdf_text_cache = {}
        
    def parse_email_date(self, msg) -> Optional[datetime]:
        """Extract date from email message."""
        date_str = msg.get('Date', '')
        try:
            parsed_date = parsedate_to_datetime(date_str)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except:
            return None
    
    def extract_email_content(self, msg) -> str:
        """Extract all text content from email."""
        content = []
        
        # Add subject
        subject = msg.get('Subject', '')
        content.append(f"Subject: {subject}")
        
        # Extract body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        content.append(body)
                    except:
                        pass
                elif part.get_content_type() == 'text/html':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Simple HTML stripping
                        body = re.sub('<[^<]+?>', '', body)
                        content.append(body)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                content.append(body)
            except:
                pass
        
        return '\n'.join(content)
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file using multiple methods."""
        if pdf_path in self.pdf_text_cache:
            return self.pdf_text_cache[pdf_path]
        
        text_content = []
        
        # Try pdfplumber first (better for tables and complex layouts)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Limit to first 20 pages to avoid timeout
                for i, page in enumerate(pdf.pages[:20]):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                if len(pdf.pages) > 20:
                    text_content.append(f"\n[PDF has {len(pdf.pages)} pages, showing first 20]")
        except Exception as e:
            print(f"pdfplumber failed for {os.path.basename(pdf_path)}: {e}")
        
        # If pdfplumber didn't get much, try PyPDF2
        if len('\n'.join(text_content)) < 100:
            try:
                reader = PdfReader(pdf_path)
                # Limit to first 20 pages
                for i, page in enumerate(reader.pages[:20]):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            except Exception as e:
                print(f"PyPDF2 failed for {os.path.basename(pdf_path)}: {e}")
        
        result = '\n'.join(text_content)[:50000]  # Limit to 50k chars per PDF
        self.pdf_text_cache[pdf_path] = result
        return result
    
    def find_pdf_attachments(self, msg, email_date: str) -> List[Tuple[str, str]]:
        """Find PDF attachments for this email."""
        pdf_attachments = []
        
        if not msg.is_multipart():
            return pdf_attachments
        
        # Extract sender domain
        from_addr = msg.get('From', '')
        sender_domain = None
        if '@' in from_addr:
            match = re.search(r'@([^\s>]+)', from_addr)
            if match:
                sender_domain = match.group(1)
        
        # Look for PDF attachments
        for part in msg.walk():
            if part.get_content_type() == 'application/pdf':
                filename = part.get_filename()
                if filename and sender_domain:
                    # Construct the expected path
                    date_prefix = email_date.replace(':', '').replace('-', '')[:8]
                    
                    # Check multiple possible paths
                    possible_paths = [
                        os.path.join(self.pdf_dir, sender_domain, filename),
                        os.path.join(self.pdf_dir, sender_domain, f"{date_prefix}*{filename}"),
                        os.path.join(self.pdf_dir, "other", filename),
                        os.path.join(self.pdf_dir, "other", f"{date_prefix}*{filename}")
                    ]
                    
                    for path_pattern in possible_paths:
                        if '*' in path_pattern:
                            # Use glob to find matching files
                            import glob
                            matches = glob.glob(path_pattern)
                            if matches:
                                pdf_attachments.append((filename, matches[0]))
                                break
                        elif os.path.exists(path_pattern):
                            pdf_attachments.append((filename, path_pattern))
                            break
        
        return pdf_attachments
    
    def index_email(self, msg, email_id: str):
        """Index a single email with its metadata and PDF attachments."""
        # Extract metadata
        email_date = self.parse_email_date(msg)
        if not email_date:
            return
        
        from_addr = msg.get('From', '')
        to_addr = msg.get('To', '')
        subject = msg.get('Subject', '')
        message_id = msg.get('Message-ID', email_id)
        in_reply_to = msg.get('In-Reply-To', '')
        
        # Extract email content
        email_content = self.extract_email_content(msg)
        
        # Find and extract PDF attachments
        pdf_texts = []
        pdf_filenames = []
        pdf_attachments = self.find_pdf_attachments(msg, email_date.isoformat())
        
        for filename, filepath in pdf_attachments:
            pdf_text = self.extract_pdf_text(filepath)
            if pdf_text:
                pdf_texts.append(f"[PDF Attachment: {filename}]\n{pdf_text}")
                pdf_filenames.append(filename)
        
        # Combine email content with PDF content
        full_content = email_content
        if pdf_texts:
            full_content += "\n\n=== PDF ATTACHMENTS ===\n\n" + "\n\n".join(pdf_texts)
        
        # Create metadata
        metadata = {
            "email_id": email_id,
            "message_id": message_id,
            "thread_id": in_reply_to if in_reply_to else message_id,
            "date": email_date.isoformat(),
            "date_year": email_date.year,
            "date_month": email_date.month,
            "date_day": email_date.day,
            "from": from_addr,
            "to": to_addr,
            "subject": subject,
            "has_pdf": len(pdf_filenames) > 0,
            "pdf_count": len(pdf_filenames),
            "pdf_filenames": json.dumps(pdf_filenames),
            "content_length": len(full_content)
        }
        
        # Add domain metadata
        if '@crestnicholson.com' in from_addr.lower():
            metadata["from_crest"] = True
        if '@nhos.org.uk' in from_addr.lower():
            metadata["from_nhos"] = True
        if 'paulroberttaylor@gmail.com' in from_addr.lower():
            metadata["from_paul"] = True
        if 'jade.millington@hotmail.co.uk' in from_addr.lower():
            metadata["from_jade"] = True
        
        # Index in ChromaDB
        try:
            self.collection.add(
                documents=[full_content],
                metadatas=[metadata],
                ids=[email_id]
            )
            self.processed_count += 1
            
            if self.processed_count % 100 == 0:
                print(f"Indexed {self.processed_count} emails...")
        except Exception as e:
            print(f"Error indexing email {email_id}: {e}")
    
    def index_all_emails(self):
        """Index all emails from the mbox file."""
        print("Opening mbox file...")
        mbox = mailbox.mbox(self.mbox_path)
        
        print("Indexing emails and PDF attachments...")
        total_emails = len(mbox)
        print(f"Total emails to process: {total_emails}")
        
        for i, msg in enumerate(mbox):
            email_id = f"email_{i}"
            self.index_email(msg, email_id)
            
            # Show progress every 50 emails
            if (i + 1) % 50 == 0:
                print(f"Progress: {i+1}/{total_emails} emails processed...")
        
        print(f"\nIndexing complete! Total emails indexed: {self.processed_count}")
        
        # Print statistics
        total_docs = self.collection.count()
        print(f"Total documents in collection: {total_docs}")
        
        # Sample query to verify
        results = self.collection.query(
            query_texts=["plot 34 contract delay"],
            n_results=3
        )
        
        print(f"\nSample search for 'plot 34 contract delay' found {len(results['ids'][0])} results")
    
    def search(self, query: str, n_results: int = 10, filters: Optional[Dict] = None) -> Dict:
        """Search the email collection."""
        where_clause = filters if filters else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        return results
    
    def search_with_display(self, query: str, n_results: int = 10, filters: Optional[Dict] = None):
        """Search and display results in a readable format."""
        results = self.search(query, n_results, filters)
        
        if not results['ids'][0]:
            print("No results found.")
            return
        
        print(f"\nFound {len(results['ids'][0])} results for: '{query}'\n")
        
        for i, (doc_id, metadata, document, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['documents'][0],
            results['distances'][0]
        )):
            print(f"Result {i+1} (relevance score: {1-distance:.3f}):")
            print(f"Date: {metadata.get('date', 'Unknown')[:10]}")
            print(f"From: {metadata.get('from', 'Unknown')}")
            print(f"To: {metadata.get('to', 'Unknown')}")
            print(f"Subject: {metadata.get('subject', 'Unknown')}")
            
            if metadata.get('has_pdf'):
                pdf_files = json.loads(metadata.get('pdf_filenames', '[]'))
                print(f"PDF Attachments: {', '.join(pdf_files)}")
            
            # Show relevant excerpt
            query_lower = query.lower()
            doc_lower = document.lower()
            
            # Find best matching section
            best_start = 0
            if query_lower in doc_lower:
                best_start = doc_lower.find(query_lower)
            
            excerpt_start = max(0, best_start - 200)
            excerpt_end = min(len(document), best_start + 300)
            excerpt = document[excerpt_start:excerpt_end]
            
            if excerpt_start > 0:
                excerpt = "..." + excerpt
            if excerpt_end < len(document):
                excerpt = excerpt + "..."
            
            print(f"Excerpt: {excerpt}")
            print("-" * 80)

def main():
    if len(sys.argv) < 2:
        print("Usage: python chromadb-email-indexer.py <mbox_file> [pdf_directory]")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    pdf_dir = sys.argv[2] if len(sys.argv) > 2 else "pdf_attachments"
    
    if not os.path.exists(mbox_path):
        print(f"Error: File '{mbox_path}' not found")
        sys.exit(1)
    
    indexer = EmailIndexer(mbox_path, pdf_dir)
    indexer.index_all_emails()
    
    # Interactive search
    print("\n\nEmail collection indexed! You can now search.")
    print("Example searches:")
    print("  - plot 34 contract delay")
    print("  - air brick buried")
    print("  - render crack")
    print("  - completion december 2023")
    print("\nType 'quit' to exit.\n")
    
    while True:
        query = input("Search query: ").strip()
        if query.lower() == 'quit':
            break
        
        if query:
            indexer.search_with_display(query)

if __name__ == "__main__":
    main()