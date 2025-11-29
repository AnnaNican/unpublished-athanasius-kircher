#!/usr/bin/env python3
"""
create_chroma_db.py
-------------------

Creates a ChromaDB database from all text files in knowledge/txt-en directory.
Initializes a persistent client, creates a collection called "kircker", and
loads all documents from the txt-en directory.
"""

from __future__ import annotations

import chromadb
from pathlib import Path


TXT_EN_DIR = Path("knowledge/txt-en")
CHROMA_DB_PATH = "chroma_tmp"
COLLECTION_NAME = "kircker"


def load_text_files(directory: Path) -> list[tuple[str, str, dict]]:
    """
    Load all .txt files from the directory.
    
    Returns:
        List of tuples: (document_id, text_content, metadata)
    """
    documents = []
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    txt_files = sorted(directory.glob("*.txt"))
    
    if not txt_files:
        raise ValueError(f"No .txt files found in {directory}")
    
    print(f"Found {len(txt_files)} text files:")
    for txt_file in txt_files:
        print(f"  - {txt_file.name}")
        content = txt_file.read_text(encoding="utf-8")
        # Use filename without extension as document ID
        doc_id = txt_file.stem
        metadata = {"source": txt_file.name, "filename": txt_file.name}
        documents.append((doc_id, content, metadata))
    
    return documents


def main() -> None:
    """Main function to create ChromaDB collection."""
    print("=" * 60)
    print("Creating ChromaDB database for Kircher texts")
    print("=" * 60)
    
    # Initialize persistent client
    print(f"\nInitializing ChromaDB client at: {CHROMA_DB_PATH}")
    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=chromadb.Settings(allow_reset=True)
    )
    
    # Reset the database
    print("Resetting database...")
    client.reset()
    
    # Create collection
    print(f"Creating collection: {COLLECTION_NAME}")
    collection = client.create_collection(name=COLLECTION_NAME)
    
    # Load all text files
    print(f"\nLoading text files from: {TXT_EN_DIR}")
    documents = load_text_files(TXT_EN_DIR)
    
    # Add documents to collection
    print(f"\nAdding {len(documents)} documents to collection...")
    for doc_id, content, metadata in documents:
        collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[metadata]
        )
        print(f"  ✓ Added: {doc_id}")
    
    # Peek at the collection
    print("\n" + "=" * 60)
    print("Collection peek:")
    print("=" * 60)
    results = collection.peek()
    print(results)
    
    print("\n" + "=" * 60)
    print(f"✓ Successfully created ChromaDB collection '{COLLECTION_NAME}'")
    print(f"  Database location: {CHROMA_DB_PATH}")
    print(f"  Total documents: {len(documents)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

