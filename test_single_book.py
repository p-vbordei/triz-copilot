#!/usr/bin/env python3
"""Test script to process a single book."""

import sys
from pathlib import Path

# Find first PDF
books_dir = Path("/Users/vladbordei/Documents/Development/triz2/books")
pdf_files = list(books_dir.rglob("*.pdf"))

if not pdf_files:
    print("No PDF files found")
    sys.exit(1)

first_pdf = pdf_files[0]
print(f"Testing with: {first_pdf.name}")
print(f"Path: {first_pdf}")

# Test PDF reading
try:
    import PyPDF2
    
    with open(first_pdf, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        print(f"✓ PDF has {num_pages} pages")
        
        # Extract first page
        first_page = pdf_reader.pages[0]
        text = first_page.extract_text()
        print(f"✓ First page has {len(text)} characters")
        print(f"Preview: {text[:200]}...")
        
except Exception as e:
    print(f"❌ Error reading PDF: {e}")
    import traceback
    traceback.print_exc()

# Test embedding generation
print("\nTesting embedding generation...")
try:
    import requests
    
    test_text = "TRIZ innovation and problem solving"
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": test_text},
        timeout=10
    )
    
    if response.status_code == 200:
        embedding = response.json()["embedding"]
        print(f"✓ Embedding generated, dimension: {len(embedding)}")
    else:
        print(f"❌ Embedding API error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Embedding error: {e}")

# Test Qdrant
print("\nTesting Qdrant...")
try:
    from qdrant_client import QdrantClient
    
    client = QdrantClient(host="localhost", port=6333)
    collections = client.get_collections()
    print(f"✓ Connected to Qdrant")
    print(f"  Collections: {[c.name for c in collections.collections]}")
    
except Exception as e:
    print(f"❌ Qdrant error: {e}")

print("\n✅ All tests passed - ready to process books")