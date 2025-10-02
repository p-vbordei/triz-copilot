#!/usr/bin/env python3
"""
TRIZ Knowledge Base Ingestion Pipeline (T047)
Ingests TRIZ principles, books, and materials into vector database.
"""

import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import hashlib

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.triz_tools.services.vector_service import get_vector_service
from src.triz_tools.services.embedding_service import get_embedding_service
from src.triz_tools.knowledge_base import load_principles_from_file
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TRIZKnowledgeIngestion:
    """Ingestion pipeline for TRIZ knowledge base"""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialize ingestion pipeline.
        
        Args:
            host: Qdrant host
            port: Qdrant port
        """
        self.vector_service = get_vector_service(host=host, port=port)
        self.embedding_service = get_embedding_service()
        self.ingested_count = 0
        
    def ingest_triz_principles(
        self,
        principles_file: Optional[Path] = None,
        collection_name: str = "triz_principles"
    ) -> bool:
        """
        Ingest TRIZ 40 principles into vector database.
        
        Args:
            principles_file: Path to principles file
            collection_name: Target collection name
        
        Returns:
            True if successful
        """
        logger.info("Ingesting TRIZ principles...")
        
        # Load principles
        knowledge_base = load_principles_from_file(principles_file)
        
        if not knowledge_base.principles:
            logger.error("No principles loaded")
            return False
        
        # Prepare vectors and payloads
        vectors = []
        payloads = []
        ids = []
        
        for principle_id, principle in knowledge_base.principles.items():
            # Generate composite embedding
            composite_text = f"{principle.principle_name}: {principle.description}"
            if principle.sub_principles:
                composite_text += " " + " ".join(principle.sub_principles[:3])
            
            embedding = self.embedding_service.generate_embedding(composite_text)
            
            if embedding is not None:
                vectors.append(embedding)
                
                # Create payload
                payload = {
                    "principle_id": principle.principle_id,
                    "principle_number": principle.principle_number,
                    "principle_name": principle.principle_name,
                    "description": principle.description,
                    "sub_principles": principle.sub_principles,
                    "examples": principle.examples[:5] if principle.examples else [],
                    "domains": principle.domains,
                    "usage_frequency": principle.usage_frequency,
                    "innovation_level": principle.innovation_level,
                    "type": "principle"
                }
                
                payloads.append(payload)
                # Use integer ID instead of string
                ids.append(int(principle.principle_number))

                logger.info(f"  Processed principle {principle_id}: {principle.principle_name}")
        
        # Insert into vector database
        if vectors:
            success = self.vector_service.insert_vectors(
                collection_name=collection_name,
                vectors=vectors,
                payloads=payloads,
                ids=ids
            )
            
            if success:
                self.ingested_count += len(vectors)
                logger.info(f"✅ Ingested {len(vectors)} TRIZ principles")
                return True
            else:
                logger.error("Failed to insert principles into vector database")
                return False
        
        return False
    
    def ingest_contradiction_matrix(
        self,
        matrix_file: Optional[Path] = None,
        collection_name: str = "triz_contradictions"
    ) -> bool:
        """
        Ingest contradiction matrix into vector database.
        
        Args:
            matrix_file: Path to matrix JSON file
            collection_name: Target collection name
        
        Returns:
            True if successful
        """
        logger.info("Ingesting contradiction matrix...")
        
        if matrix_file is None:
            matrix_file = Path(__file__).parent.parent / "data" / "contradiction_matrix.json"
        
        if not matrix_file.exists():
            logger.warning(f"Matrix file not found: {matrix_file}")
            return False
        
        # Load matrix data
        with open(matrix_file, "r") as f:
            matrix_data = json.load(f)
        
        vectors = []
        payloads = []
        ids = []
        counter = 0

        # Process matrix entries (it's a list, not a dict)
        for entry_data in matrix_data.get("matrix", []):
            # Generate embedding for contradiction description
            improving = entry_data.get("improving", 0)
            worsening = entry_data.get("worsening", 0)
            principles = entry_data.get("principles", [])
            
            text = f"Improving parameter {improving} while worsening parameter {worsening}. "
            text += f"Recommended principles: {', '.join(map(str, principles))}"
            
            embedding = self.embedding_service.generate_embedding(text)
            
            if embedding is not None:
                vectors.append(embedding)
                
                payload = {
                    "improving_parameter": improving,
                    "worsening_parameter": worsening,
                    "recommended_principles": principles,
                    "confidence": entry_data.get("confidence", 0.7),
                    "applications": entry_data.get("applications", 0),
                    "type": "contradiction"
                }
                
                payloads.append(payload)
                # Use integer counter for IDs
                counter += 1
                ids.append(counter)
        
        # Insert into vector database
        if vectors:
            success = self.vector_service.insert_vectors(
                collection_name=collection_name,
                vectors=vectors,
                payloads=payloads,
                ids=ids
            )
            
            if success:
                self.ingested_count += len(vectors)
                logger.info(f"✅ Ingested {len(vectors)} contradiction entries")
                return True
        
        return False
    
    def ingest_pdf_content(
        self,
        pdf_path: Path,
        collection_name: str = "triz_documents",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> bool:
        """
        Ingest PDF content into vector database.
        
        Args:
            pdf_path: Path to PDF file
            collection_name: Target collection name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        
        Returns:
            True if successful
        """
        try:
            import PyPDF2
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return False
        
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return False
        
        logger.info(f"Ingesting PDF: {pdf_path.name}")
        
        try:
            # Extract text from PDF
            text_content = ""
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text()
            
            # Clean text
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = re.sub(r'\n+', '\n', text_content)
            
            # Create chunks
            chunks = self._create_chunks(text_content, chunk_size, chunk_overlap)
            
            # Generate embeddings and prepare data
            vectors = []
            payloads = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:  # Skip very short chunks
                    continue
                
                embedding = self.embedding_service.generate_embedding(chunk)
                
                if embedding is not None:
                    vectors.append(embedding)
                    
                    # Create unique ID
                    chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
                    doc_id = f"doc_{pdf_path.stem}_{i}_{chunk_hash}"
                    
                    payload = {
                        "document_name": pdf_path.name,
                        "document_path": str(pdf_path),
                        "chunk_index": i,
                        "chunk_text": chunk[:500],  # Store first 500 chars
                        "chunk_size": len(chunk),
                        "type": "document_chunk"
                    }
                    
                    # Check if TRIZ-related
                    triz_keywords = ["triz", "inventive", "contradiction", "principle", "innovation"]
                    if any(keyword in chunk.lower() for keyword in triz_keywords):
                        payload["is_triz_related"] = True
                    
                    payloads.append(payload)
                    ids.append(doc_id)
            
            # Insert into vector database
            if vectors:
                success = self.vector_service.insert_vectors(
                    collection_name=collection_name,
                    vectors=vectors,
                    payloads=payloads,
                    ids=ids
                )
                
                if success:
                    self.ingested_count += len(vectors)
                    logger.info(f"✅ Ingested {len(vectors)} chunks from {pdf_path.name}")
                    return True
            
        except Exception as e:
            logger.error(f"Failed to ingest PDF: {str(e)}")
            return False
        
        return False
    
    def _create_chunks(
        self,
        text: str,
        chunk_size: int,
        overlap: int
    ) -> List[str]:
        """Create overlapping text chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.8:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def ingest_directory(
        self,
        directory_path: Path,
        pattern: str = "*.pdf",
        collection_name: str = "triz_documents",
        max_files: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Ingest all matching files from a directory.
        
        Args:
            directory_path: Directory to scan
            pattern: File pattern to match
            collection_name: Target collection
            max_files: Maximum files to process
        
        Returns:
            Dictionary with file paths and success status
        """
        results = {}
        
        if not directory_path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return results
        
        # Find matching files
        files = list(directory_path.rglob(pattern))
        
        if max_files:
            files = files[:max_files]
        
        logger.info(f"Found {len(files)} files to ingest")
        
        for file_path in files:
            logger.info(f"\nProcessing: {file_path.name}")
            
            if file_path.suffix.lower() == ".pdf":
                success = self.ingest_pdf_content(
                    file_path,
                    collection_name=collection_name
                )
                results[str(file_path)] = success
        
        # Summary
        successful = sum(1 for s in results.values() if s)
        logger.info(f"\n✅ Successfully ingested {successful}/{len(results)} files")
        logger.info(f"Total items ingested: {self.ingested_count}")
        
        return results


def main():
    """Main ingestion function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest TRIZ knowledge into vector DB")
    parser.add_argument("--host", default="localhost", help="Qdrant host")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant port")
    parser.add_argument("--principles", action="store_true", help="Ingest TRIZ principles")
    parser.add_argument("--matrix", action="store_true", help="Ingest contradiction matrix")
    parser.add_argument("--pdf", type=str, help="Ingest specific PDF file")
    parser.add_argument("--directory", type=str, help="Ingest directory of PDFs")
    parser.add_argument("--max-files", type=int, help="Maximum files to process")
    
    args = parser.parse_args()
    
    # Create ingestion pipeline
    pipeline = TRIZKnowledgeIngestion(host=args.host, port=args.port)
    
    # Check if vector service is available
    if not pipeline.vector_service.is_available():
        logger.error("Vector database not available. Start Qdrant first.")
        sys.exit(1)
    
    # Run ingestion tasks
    if args.principles:
        pipeline.ingest_triz_principles()
    
    if args.matrix:
        pipeline.ingest_contradiction_matrix()
    
    if args.pdf:
        pdf_path = Path(args.pdf)
        pipeline.ingest_pdf_content(pdf_path)
    
    if args.directory:
        dir_path = Path(args.directory)
        pipeline.ingest_directory(
            dir_path,
            max_files=args.max_files
        )
    
    if not any([args.principles, args.matrix, args.pdf, args.directory]):
        # Default: ingest principles and matrix
        logger.info("No specific task specified. Ingesting principles and matrix...")
        pipeline.ingest_triz_principles()
        pipeline.ingest_contradiction_matrix()
    
    logger.info(f"\n🎉 Ingestion complete! Total items: {pipeline.ingested_count}")


if __name__ == "__main__":
    main()