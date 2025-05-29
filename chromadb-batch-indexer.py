#!/usr/bin/env python3
"""
Batch-based ChromaDB Email Indexer
Processes emails in batches to avoid timeouts and allows resuming
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
import pickle
import time
import warnings
warnings.filterwarnings("ignore")

class BatchEmailIndexer:
    def __init__(self, mbox_path: str, pdf_dir: str = "pdf_attachments", batch_size: int = 50):
        self.mbox_path = mbox_path
        self.pdf_dir = pdf_dir
        self.batch_size = batch_size
        self.state_file = "indexer_state.pkl"
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails")
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(
                name="crest_emails",
                embedding_function=self.embedding_function
            )
            print(f"Found existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="crest_emails",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            print("Created new collection")
        
        # Load state if exists
        self.state = self.load_state()
        self.pdf_text_cache = self.state.get('pdf_cache', {})
        self.processed_emails = self.state.get('processed_emails', set())
        self.last_index = self.state.get('last_index', 0)
        
    def load_state(self) -> Dict:
        """Load previous indexing state if exists."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def save_state(self):
        """Save current indexing state."""
        state = {
            'pdf_cache': self.pdf_text_cache,
            'processed_emails': self.processed_emails,
            'last_index': self.last_index
        }
        with open(self.state_file, 'wb') as f:
            pickle.dump(state, f)
    
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
        """Extract text content from email - simplified version."""
        content = []
        
        # Add subject
        subject = msg.get('Subject', '')
        content.append(f"Subject: {subject}")
        
        # Extract body - only plain text to save time
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        content.append(body[:5000])  # Limit body size
                        break  # Take first plain text part only
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                content.append(body[:5000])
            except:
                pass
        
        return '\n'.join(content)
    
    def extract_pdf_text_quick(self, pdf_path: str) -> str:
        """Quick PDF text extraction - first 5 pages only."""
        if pdf_path in self.pdf_text_cache:
            return self.pdf_text_cache[pdf_path]
        
        text_content = []
        
        try:
            # Use PyPDF2 for speed
            reader = PdfReader(pdf_path)
            # Only first 5 pages
            for i, page in enumerate(reader.pages[:5]):
                if i >= 5:
                    break
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except:
                    continue
                    
            if len(reader.pages) > 5:
                text_content.append(f"\n[PDF has {len(reader.pages)} pages, indexed first 5]")
        except Exception as e:
            # Silently skip problematic PDFs
            pass
        
        result = '\n'.join(text_content)[:10000]  # Limit to 10k chars
        self.pdf_text_cache[pdf_path] = result
        return result
    
    def find_pdf_attachments_quick(self, msg) -> List[Tuple[str, str]]:
        """Quick PDF attachment finder."""
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
                    # Simple path check
                    path = os.path.join(self.pdf_dir, sender_domain, filename)
                    if os.path.exists(path):
                        pdf_attachments.append((filename, path))
                    else:
                        # Try other folder
                        path = os.path.join(self.pdf_dir, "other", filename)
                        if os.path.exists(path):
                            pdf_attachments.append((filename, path))
        
        return pdf_attachments[:3]  # Limit to 3 PDFs per email
    
    def index_email_batch(self, emails: List[Tuple[int, email.message.Message]]):
        """Index a batch of emails."""
        documents = []
        metadatas = []
        ids = []
        
        for idx, msg in emails:
            email_id = f"email_{idx}"
            
            # Skip if already processed
            if email_id in self.processed_emails:
                continue
            
            # Extract metadata
            email_date = self.parse_email_date(msg)
            if not email_date:
                continue
            
            from_addr = msg.get('From', '')
            to_addr = msg.get('To', '')
            subject = msg.get('Subject', '')
            message_id = msg.get('Message-ID', email_id)
            in_reply_to = msg.get('In-Reply-To', '')
            
            # Extract email content
            email_content = self.extract_email_content(msg)
            
            # Find PDFs but don't extract text yet
            pdf_attachments = self.find_pdf_attachments_quick(msg)
            pdf_filenames = [f[0] for f in pdf_attachments]
            
            # For now, just note that PDFs exist
            if pdf_filenames:
                email_content += f"\n\n[Has PDF attachments: {', '.join(pdf_filenames)}]"
            
            # Create metadata
            metadata = {
                "email_id": email_id,
                "message_id": message_id[:100],  # Limit length
                "thread_id": (in_reply_to if in_reply_to else message_id)[:100],
                "date": email_date.isoformat(),
                "date_year": email_date.year,
                "date_month": email_date.month,
                "date_day": email_date.day,
                "from": from_addr[:200],
                "to": to_addr[:200],
                "subject": subject[:200],
                "has_pdf": len(pdf_filenames) > 0,
                "pdf_count": len(pdf_filenames)
            }
            
            # Add domain flags
            from_lower = from_addr.lower()
            if '@crestnicholson.com' in from_lower:
                metadata["from_crest"] = True
            if '@nhos.org.uk' in from_lower:
                metadata["from_nhos"] = True
            if 'paulroberttaylor@gmail.com' in from_lower:
                metadata["from_paul"] = True
            if 'jade.millington@hotmail.co.uk' in from_lower:
                metadata["from_jade"] = True
            
            documents.append(email_content)
            metadatas.append(metadata)
            ids.append(email_id)
            self.processed_emails.add(email_id)
        
        # Batch add to ChromaDB
        if documents:
            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"  Indexed batch of {len(documents)} emails")
            except Exception as e:
                print(f"  Error indexing batch: {e}")
    
    def index_all_emails(self):
        """Index all emails in batches."""
        print("Opening mbox file...")
        mbox = mailbox.mbox(self.mbox_path)
        
        # Count total
        print("Counting emails...")
        total_emails = len(mbox)
        print(f"Total emails: {total_emails}")
        print(f"Starting from index: {self.last_index}")
        
        # Process in batches
        batch = []
        batch_num = 0
        
        for i, msg in enumerate(mbox):
            # Skip already processed
            if i < self.last_index:
                continue
            
            batch.append((i, msg))
            
            # Process batch when full
            if len(batch) >= self.batch_size:
                batch_num += 1
                print(f"\nProcessing batch {batch_num} (emails {i-self.batch_size+1} to {i})...")
                
                start_time = time.time()
                self.index_email_batch(batch)
                batch_time = time.time() - start_time
                
                print(f"  Batch took {batch_time:.1f} seconds")
                
                # Update state
                self.last_index = i + 1
                self.save_state()
                
                # Clear batch
                batch = []
                
                # Show progress
                progress = (i + 1) / total_emails * 100
                print(f"  Overall progress: {i+1}/{total_emails} ({progress:.1f}%)")
        
        # Process final batch
        if batch:
            print(f"\nProcessing final batch...")
            self.index_email_batch(batch)
            self.last_index = total_emails
            self.save_state()
        
        print(f"\nIndexing complete!")
        print(f"Total documents in collection: {self.collection.count()}")
        
        # Clean up state file
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
            print("Cleaned up state file")

def main():
    if len(sys.argv) < 2:
        print("Usage: python chromadb-batch-indexer.py <mbox_file> [batch_size]")
        print("Default batch_size is 50")
        sys.exit(1)
    
    mbox_path = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if not os.path.exists(mbox_path):
        print(f"Error: File '{mbox_path}' not found")
        sys.exit(1)
    
    indexer = BatchEmailIndexer(mbox_path, batch_size=batch_size)
    
    try:
        indexer.index_all_emails()
    except KeyboardInterrupt:
        print("\n\nIndexing interrupted! State saved.")
        print("Run the script again to resume from where you left off.")
        indexer.save_state()
    except Exception as e:
        print(f"\nError: {e}")
        print("State saved. You can resume by running the script again.")
        indexer.save_state()

if __name__ == "__main__":
    main()