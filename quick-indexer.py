#!/usr/bin/env python3
"""
Quick Email Indexer - Just the basics for fast searching
"""

import mailbox
import email
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import os
import sys
import chromadb
from chromadb.utils import embedding_functions
import pickle

class QuickIndexer:
    def __init__(self, mbox_path: str):
        self.mbox_path = mbox_path
        self.state_file = "quick_indexer_state.pkl"
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chromadb_emails_quick")
        
        # Use sentence transformer for better performance
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(
                name="emails_quick",
                embedding_function=self.embedding_function
            )
            print(f"Found existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="emails_quick",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            print("Created new collection")
        
        self.last_index = self.load_state()
    
    def load_state(self) -> int:
        """Load last processed index."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return 0
        return 0
    
    def save_state(self, index: int):
        """Save current index."""
        with open(self.state_file, 'wb') as f:
            pickle.dump(index, f)
    
    def quick_process(self):
        """Process emails as fast as possible."""
        print("Opening mbox...")
        mbox = mailbox.mbox(self.mbox_path)
        
        batch_size = 200
        batch_docs = []
        batch_metas = []
        batch_ids = []
        
        print(f"Starting from index {self.last_index}")
        
        for i, msg in enumerate(mbox):
            if i < self.last_index:
                continue
            
            # Quick extract
            try:
                date = msg.get('Date', '')
                from_addr = msg.get('From', '')
                to_addr = msg.get('To', '')
                subject = msg.get('Subject', '')
                
                # Simple content
                content = f"Subject: {subject}\nFrom: {from_addr}\nTo: {to_addr}\nDate: {date}\n"
                
                # Quick body extract
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                content += body[:2000]
                                break
                            except:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        content += body[:2000]
                    except:
                        pass
                
                # Quick metadata
                meta = {
                    "id": i,
                    "subject": subject[:200],
                    "from": from_addr[:100],
                    "to": to_addr[:100],
                    "date": date[:50]
                }
                
                batch_docs.append(content)
                batch_metas.append(meta)
                batch_ids.append(f"e{i}")
                
                # Process batch
                if len(batch_docs) >= batch_size:
                    print(f"Indexing batch at {i} ({i/1723*100:.1f}%)...")
                    try:
                        self.collection.add(
                            documents=batch_docs,
                            metadatas=batch_metas,
                            ids=batch_ids
                        )
                    except:
                        pass
                    
                    # Clear and save
                    batch_docs = []
                    batch_metas = []
                    batch_ids = []
                    self.save_state(i)
                    
            except:
                continue
        
        # Final batch
        if batch_docs:
            print("Indexing final batch...")
            try:
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
            except:
                pass
        
        print(f"Done! Indexed {self.collection.count()} emails")
        
        # Clean up
        if os.path.exists(self.state_file):
            os.remove(self.state_file)

def main():
    if len(sys.argv) != 2:
        print("Usage: python quick-indexer.py <mbox_file>")
        sys.exit(1)
    
    indexer = QuickIndexer(sys.argv[1])
    
    try:
        indexer.quick_process()
    except KeyboardInterrupt:
        print("\nInterrupted! Run again to resume.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()