#!/usr/bin/env python3
"""Fast book ingestion - processes first few pages only for testing."""

import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict
import requests
from datetime import datetime

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    import PyPDF2
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

def main():
    print("="*60)
    print("TRIZ Books Fast Ingestion (First 3 pages per book)")
    print("="*60)
    
    # Setup
    books_dir = Path("/Users/vladbordei/Documents/Development/triz2/books")
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "triz_books"
    
    # Initialize collection
    collections = client.get_collections()
    if collection_name in [c.name for c in collections.collections]:
        print(f"Deleting existing collection '{collection_name}'...")
        client.delete_collection(collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print(f"✓ Created collection '{collection_name}'")
    
    # Find PDFs only (faster than processing EPUBs)
    pdf_files = list(books_dir.rglob("*.pdf"))[:5]  # Process only first 5 PDFs
    print(f"\n📚 Processing {len(pdf_files)} PDF files (first 3 pages each)")
    
    total_chunks = 0
    
    for pdf_path in pdf_files:
        print(f"\n📖 {pdf_path.name}")
        
        try:
            # Extract text from first 3 pages
            text_parts = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_to_read = min(3, len(pdf_reader.pages))
                
                for page_num in range(pages_to_read):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"Page {page_num + 1}: {text}")
            
            if not text_parts:
                print("  ⚠️ No text extracted")
                continue
            
            full_text = "\n\n".join(text_parts)
            print(f"  Extracted {len(full_text)} characters from {len(text_parts)} pages")
            
            # Create one chunk per page
            points = []
            for i, page_text in enumerate(text_parts):
                # Truncate to reasonable size
                chunk_text = page_text[:2000]
                
                # Generate embedding
                print(f"  Generating embedding for page {i+1}...", end="", flush=True)
                response = requests.post(
                    "http://localhost:11434/api/embeddings",
                    json={"model": "nomic-embed-text", "prompt": chunk_text},
                    timeout=30
                )
                
                if response.status_code == 200:
                    embedding = response.json()["embedding"]
                    
                    # Create unique ID (use integer hash)
                    chunk_id = abs(hash(f"{pdf_path.name}_{i}")) % (10**12)
                    
                    point = PointStruct(
                        id=chunk_id,
                        vector=embedding,
                        payload={
                            "file_name": pdf_path.name,
                            "file_path": str(pdf_path.relative_to(books_dir)),
                            "page": i + 1,
                            "text": chunk_text[:500],  # Store preview only
                            "type": "book"
                        }
                    )
                    points.append(point)
                    print(" ✓")
                else:
                    print(f" ❌ (status {response.status_code})")
            
            # Upload to Qdrant
            if points:
                client.upsert(collection_name=collection_name, points=points)
                print(f"  ✓ Uploaded {len(points)} vectors")
                total_chunks += len(points)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Summary: Processed {len(pdf_files)} books, created {total_chunks} vectors")
    
    # Test search
    if total_chunks > 0:
        print(f"\n{'='*60}")
        print("Testing Search")
        print(f"{'='*60}")
        
        test_query = "TRIZ innovation problem solving"
        print(f"Query: '{test_query}'")
        
        # Generate embedding
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": test_query},
            timeout=30
        )
        
        if response.status_code == 200:
            query_vector = response.json()["embedding"]
            
            # Search
            results = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=3
            )
            
            print("\nTop 3 results:")
            for i, result in enumerate(results.points, 1):
                p = result.payload
                print(f"\n{i}. Score: {result.score:.3f}")
                print(f"   File: {p.get('file_name', 'Unknown')}")
                print(f"   Page: {p.get('page', '?')}")
                print(f"   Preview: {p.get('text', '')[:100]}...")

if __name__ == "__main__":
    main()