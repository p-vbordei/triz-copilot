#!/usr/bin/env python3
"""
TRIZ Document Ingestion Pipeline
Ingests PDF/EPUB books into triz_documents collection for deep research.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import hashlib

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.triz_tools.services.vector_service import get_vector_service
from src.triz_tools.services.embedding_service import get_embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentIngestion:
    """Ingestion pipeline for TRIZ books and documents"""

    def __init__(self):
        self.vector_service = get_vector_service()
        self.embedding_service = get_embedding_service()
        self.collection_name = "triz_documents"
        self.ingested_count = 0

        # Ensure collection exists
        self.vector_service.create_collection(
            collection_name=self.collection_name, vector_size=768, on_disk=False
        )
        logger.info("Document ingestion initialized")

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            import PyPDF2

            text = []
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n".join(text)
        except ImportError:
            logger.error("PyPDF2 not installed. Run: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            return ""

    def chunk_text(
        self, text: str, chunk_size: int = 8000, overlap: int = 1000
    ) -> List[str]:
        """
        Split text into overlapping chunks for better context.
        Large chunks (8000 chars ≈ 2000 tokens) preserve complete TRIZ concepts.

        Args:
            text: Full document text
            chunk_size: Target chunk size in characters (default 8000 = ~2000 tokens)
            overlap: Overlap between chunks (default 1000 chars)

        Returns:
            List of text chunks
        """
        # Clean text
        text = re.sub(r"\s+", " ", text).strip()

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary (search back up to 1000 chars)
            if end < len(text):
                # Look for period, question mark, or exclamation
                for i in range(end, max(start + chunk_size - 1000, start), -1):
                    if text[i] in ".!?":
                        end = i + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def ingest_pdf(
        self, pdf_path: Path, book_name: Optional[str] = None, category: str = "TRIZ"
    ) -> int:
        """
        Ingest a PDF book into the vector database.

        Args:
            pdf_path: Path to PDF file
            book_name: Display name for the book
            category: Book category

        Returns:
            Number of chunks ingested
        """
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return 0

        book_name = book_name or pdf_path.stem
        logger.info(f"Processing: {book_name}")

        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.error(f"No text extracted from {pdf_path}")
            return 0

        logger.info(f"Extracted {len(text)} characters")

        # Chunk text
        chunks = self.chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks")

        # Generate embeddings and store
        vectors = []
        payloads = []
        ids = []

        for i, chunk in enumerate(chunks):
            embedding = self.embedding_service.generate_embedding(chunk)

            if embedding is not None:
                vectors.append(embedding)

                # Generate unique ID
                chunk_id = abs(hash(f"{book_name}_{i}")) % (10**9)
                ids.append(chunk_id)

                # Create payload
                payloads.append(
                    {
                        "document_name": book_name,
                        "category": category,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "content": chunk[:500],  # Store first 500 chars
                        "full_content": chunk,
                        "source_file": str(pdf_path),
                    }
                )

                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(chunks)} chunks")

        # Insert into vector database
        if vectors:
            success = self.vector_service.insert_vectors(
                collection_name=self.collection_name,
                vectors=vectors,
                payloads=payloads,
                ids=ids,
            )

            if success:
                self.ingested_count += len(vectors)
                logger.info(f"✅ Ingested {len(vectors)} chunks from {book_name}")
                return len(vectors)

        return 0

    def ingest_directory(
        self, directory: Path, pattern: str = "*.pdf", category: str = "TRIZ"
    ) -> int:
        """
        Ingest all PDFs from a directory.

        Args:
            directory: Directory path
            pattern: File pattern
            category: Category for all books

        Returns:
            Total chunks ingested
        """
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return 0

        total = 0

        for pdf_file in directory.glob(pattern):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Processing: {pdf_file.name}")
            logger.info(f"{'=' * 60}")

            count = self.ingest_pdf(pdf_file, category=category)
            total += count

        return total


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest TRIZ documents")
    parser.add_argument("--pdf", type=Path, help="Single PDF file to ingest")
    parser.add_argument("--directory", type=Path, help="Directory containing PDFs")
    parser.add_argument("--category", default="TRIZ", help="Category for documents")
    parser.add_argument(
        "--triz-books",
        action="store_true",
        help="Ingest TRIZ books from default location",
    )
    parser.add_argument(
        "--collection",
        default="triz_documents",
        help="Target collection name (default: triz_documents)",
    )

    args = parser.parse_args()

    ingestion = DocumentIngestion()

    # Override collection name if specified
    if args.collection:
        ingestion.collection_name = args.collection

    if args.triz_books:
        # Ingest the two main TRIZ books
        books_dir = (
            Path(__file__).parent.parent.parent.parent
            / "books"
            / "Product Discovery and Vision"
        )

        triz_books = [
            books_dir / "TRIZ_For_Dummies_-_Lilly_Haines-Gadd.pdf",
            books_dir / "TRIZ_in_Latin_America_-_Guillermo_Cortes_Robles.pdf",
        ]

        total = 0
        for book_path in triz_books:
            if book_path.exists():
                count = ingestion.ingest_pdf(book_path, category="TRIZ")
                total += count
            else:
                logger.warning(f"Book not found: {book_path}")

        print(f"\n✅ Total TRIZ book chunks ingested: {total}")

    elif args.pdf:
        count = ingestion.ingest_pdf(args.pdf, category=args.category)
        print(f"Ingested {count} chunks from {args.pdf}")

    elif args.directory:
        count = ingestion.ingest_directory(args.directory, category=args.category)
        print(f"Ingested {count} chunks from {args.directory}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
