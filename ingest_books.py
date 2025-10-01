#!/usr/bin/env python3
"""
Recursive book ingestion script for TRIZ knowledge base.
Processes PDF, EPUB, and TXT files from books directory and subdirectories.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("Error: qdrant-client not installed. Run: pip3 install qdrant-client")
    sys.exit(1)

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
    print("Warning: PyPDF2 not installed. PDF processing will be limited.")

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    ebooklib = None
    print("Warning: ebooklib not installed. EPUB processing will be limited.")

class BookIngestion:
    def __init__(self, books_dir: str = "books", collection_name: str = "triz_books"):
        self.books_dir = Path(books_dir)
        self.collection_name = collection_name
        
        # Connect to Qdrant
        self.client = QdrantClient(host="localhost", port=6333)
        
        # Ollama settings
        self.ollama_url = "http://localhost:11434/api/embeddings"
        self.model = "nomic-embed-text"
        
        # Processing settings
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
        
        # Stats
        self.stats = {
            "files_found": 0,
            "files_processed": 0,
            "chunks_created": 0,
            "errors": []
        }
        
    def initialize_collection(self):
        """Create or recreate the collection."""
        collections = self.client.get_collections()
        
        if self.collection_name in [c.name for c in collections.collections]:
            print(f"Collection '{self.collection_name}' exists. Deleting and recreating...")
            self.client.delete_collection(self.collection_name)
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        print(f"✓ Created collection '{self.collection_name}'")
    
    def find_books(self) -> List[Path]:
        """Recursively find all book files."""
        extensions = ['.pdf', '.epub', '.txt']
        books = []
        
        for ext in extensions:
            books.extend(self.books_dir.rglob(f"*{ext}"))
        
        # Filter out hidden files and system files
        books = [b for b in books if not any(part.startswith('.') for part in b.parts)]
        
        print(f"\n📚 Found {len(books)} books:")
        for book in books:
            rel_path = book.relative_to(self.books_dir)
            print(f"  - {rel_path}")
        
        self.stats["files_found"] = len(books)
        return books
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        if PyPDF2 is None:
            return f"[PDF content from {file_path.name} - PyPDF2 not installed]"
        
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
            return '\n'.join(text)
        except Exception as e:
            print(f"  ⚠️ Error reading PDF {file_path.name}: {e}")
            return f"[Error reading PDF: {file_path.name}]"
    
    def extract_text_from_epub(self, file_path: Path) -> str:
        """Extract text from EPUB file."""
        if ebooklib is None:
            return f"[EPUB content from {file_path.name} - ebooklib not installed]"
        
        try:
            book = epub.read_epub(file_path)
            text = []
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # Basic HTML stripping
                    content = item.get_content().decode('utf-8')
                    # Remove HTML tags (simple approach)
                    import re
                    clean_text = re.sub('<[^<]+?>', '', content)
                    text.append(clean_text)
            
            return '\n'.join(text)
        except Exception as e:
            print(f"  ⚠️ Error reading EPUB {file_path.name}: {e}")
            return f"[Error reading EPUB: {file_path.name}]"
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"  ⚠️ Error reading TXT {file_path.name}: {e}")
            return f"[Error reading TXT: {file_path.name}]"
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text based on file type."""
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.epub':
            return self.extract_text_from_epub(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            return ""
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into overlapping chunks."""
        chunks = []
        
        # Clean text
        text = ' '.join(text.split())  # Normalize whitespace
        
        if len(text) <= self.chunk_size:
            chunks.append({
                "text": text,
                "chunk_index": 0,
                "total_chunks": 1,
                **metadata
            })
        else:
            # Create overlapping chunks
            start = 0
            chunk_index = 0
            
            while start < len(text):
                end = start + self.chunk_size
                
                # Try to break at sentence boundary
                if end < len(text):
                    # Look for sentence end
                    for sep in ['. ', '! ', '? ', '\n\n', '\n']:
                        pos = text.rfind(sep, start, end)
                        if pos != -1:
                            end = pos + len(sep)
                            break
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append({
                        "text": chunk,
                        "chunk_index": chunk_index,
                        "total_chunks": -1,  # Will update later
                        **metadata
                    })
                    chunk_index += 1
                
                start = end - self.chunk_overlap
                if start <= 0:
                    start = end
            
            # Update total chunks count
            for chunk in chunks:
                chunk["total_chunks"] = len(chunks)
        
        return chunks
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using Ollama."""
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model, "prompt": text},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                print(f"  ⚠️ Embedding API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ⚠️ Embedding generation error: {e}")
            return None
    
    def process_book(self, file_path: Path) -> int:
        """Process a single book file."""
        print(f"\n📖 Processing: {file_path.name}")
        
        # Extract metadata
        rel_path = file_path.relative_to(self.books_dir)
        metadata = {
            "file_name": file_path.name,
            "file_path": str(rel_path),
            "file_type": file_path.suffix.lower(),
            "folder": str(rel_path.parent) if rel_path.parent != Path('.') else "root",
            "processed_at": datetime.now().isoformat(),
            "type": "book"
        }
        
        # Extract text
        print(f"  Extracting text...")
        text = self.extract_text(file_path)
        
        if not text or len(text.strip()) < 100:
            print(f"  ⚠️ No valid text extracted")
            self.stats["errors"].append(f"No text: {file_path.name}")
            return 0
        
        print(f"  Extracted {len(text)} characters")
        
        # Create chunks
        print(f"  Creating chunks...")
        chunks = self.chunk_text(text, metadata)
        print(f"  Created {len(chunks)} chunks")
        
        # Generate embeddings and create points
        points = []
        for i, chunk in enumerate(chunks):
            # Generate unique ID
            chunk_id = hashlib.md5(
                f"{file_path.name}_{i}".encode()
            ).hexdigest()[:16]
            
            # Generate embedding
            embedding = self.generate_embedding(chunk["text"][:2000])  # Limit text length
            
            if embedding:
                point = PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload=chunk
                )
                points.append(point)
                
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(chunks)} chunks")
        
        # Upload to Qdrant
        if points:
            print(f"  Uploading {len(points)} vectors to Qdrant...")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"  ✓ Successfully processed {file_path.name}")
            self.stats["chunks_created"] += len(points)
            return len(points)
        else:
            print(f"  ⚠️ No embeddings generated")
            self.stats["errors"].append(f"No embeddings: {file_path.name}")
            return 0
    
    def run(self):
        """Run the full ingestion pipeline."""
        print("="*60)
        print("TRIZ Books Ingestion Pipeline")
        print("="*60)
        
        # Check if books directory exists
        if not self.books_dir.exists():
            print(f"❌ Books directory not found: {self.books_dir}")
            return
        
        # Initialize collection
        self.initialize_collection()
        
        # Find books
        books = self.find_books()
        
        if not books:
            print("\n❌ No books found in the directory")
            return
        
        # Process each book
        for book in books:
            try:
                chunks = self.process_book(book)
                if chunks > 0:
                    self.stats["files_processed"] += 1
            except Exception as e:
                print(f"  ❌ Error processing {book.name}: {e}")
                self.stats["errors"].append(f"Processing error: {book.name}")
        
        # Print summary
        print("\n" + "="*60)
        print("Ingestion Summary")
        print("="*60)
        print(f"📚 Files found: {self.stats['files_found']}")
        print(f"✅ Files processed: {self.stats['files_processed']}")
        print(f"📄 Chunks created: {self.stats['chunks_created']}")
        
        if self.stats["errors"]:
            print(f"\n⚠️ Errors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                print(f"  - {error}")
        
        # Test search
        if self.stats["chunks_created"] > 0:
            self.test_search()
    
    def test_search(self):
        """Test the vector search with a sample query."""
        print("\n" + "="*60)
        print("Testing Vector Search")
        print("="*60)
        
        test_query = "innovation and problem solving"
        print(f"Query: '{test_query}'")
        
        # Generate embedding for query
        embedding = self.generate_embedding(test_query)
        
        if embedding:
            # Search
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                limit=3
            )
            
            print("\nTop 3 results:")
            for i, result in enumerate(results.points, 1):
                payload = result.payload
                text_preview = payload.get('text', '')[:100] + "..."
                print(f"\n{i}. Score: {result.score:.3f}")
                print(f"   File: {payload.get('file_name', 'Unknown')}")
                print(f"   Chunk: {payload.get('chunk_index', 0) + 1}/{payload.get('total_chunks', 1)}")
                print(f"   Preview: {text_preview}")

if __name__ == "__main__":
    # Run ingestion
    ingestion = BookIngestion(
        books_dir="/Users/vladbordei/Documents/Development/triz2/books",
        collection_name="triz_books"
    )
    ingestion.run()