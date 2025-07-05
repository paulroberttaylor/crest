#!/usr/bin/env python3
import chromadb
from chromadb.config import Settings

# Try different paths
paths = ["chromadb_emails_quick", "chromadb_emails"]

for path in paths:
    try:
        print(f"\nChecking {path}:")
        client = chromadb.PersistentClient(
            path=path,
            settings=Settings(anonymized_telemetry=False)
        )
        collections = client.list_collections()
        print(f"Collections found: {[c.name for c in collections]}")
        for c in collections:
            print(f"  - {c.name}: {c.count()} documents")
    except Exception as e:
        print(f"Error: {e}")