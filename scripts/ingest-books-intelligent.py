#!/usr/bin/env python3
"""
Intelligent Book Ingestion Script
Ingests books with smart chunking, metadata extraction, and cross-referencing.
"""

import sys
import logging
from pathlib import Path
import argparse

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.triz_tools.services.vector_service import get_vector_service
from src.triz_tools.services.embedding_service import get_embedding_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion function"""
    parser = argparse.ArgumentParser(
        description="Intelligently ingest books into Qdrant vector database"
    )
    parser.add_argument(
        "--books-dir",
        type=str,
        default="books",
        help="Directory containing books (default: books)"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="triz_documents",
        help="Target collection name (default: triz_documents)"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum number of files to process"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Test mode - only process 3 files"
    )

    args = parser.parse_args()

    books_dir = Path(args.books_dir)

    if not books_dir.exists():
        logger.error(f"Books directory not found: {books_dir}")
        return 1

    # Initialize services
    logger.info("Initializing vector and embedding services...")
    vector_service = get_vector_service()
    embedding_service = get_embedding_service()

    if not vector_service.is_available():
        logger.error("Vector service not available. Start Qdrant first:")
        logger.error("  docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant")
        return 1

    # Create collection if it doesn't exist
    logger.info(f"Creating/verifying collection '{args.collection}'...")
    vector_service.create_collection(
        collection_name=args.collection,
        vector_size=768,  # nomic-embed-text dimension
        on_disk=True  # Store on disk to save RAM
    )

    # Find all PDF files
    pdf_files = list(books_dir.rglob("*.pdf"))

    if args.test_mode:
        pdf_files = pdf_files[:3]
        logger.info("TEST MODE: Only processing 3 files")
    elif args.max_files:
        pdf_files = pdf_files[:args.max_files]

    logger.info(f"Found {len(pdf_files)} PDF files to process")

    # Import the ingestion pipeline
    from src.triz_tools.setup.knowledge_ingestion import TRIZKnowledgeIngestion

    pipeline = TRIZKnowledgeIngestion()

    # Process each file
    success_count = 0
    fail_count = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        logger.info(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")

        try:
            success = pipeline.ingest_pdf_content(
                pdf_path=pdf_path,
                collection_name=args.collection,
                chunk_size=1000,  # ~500-700 words
                chunk_overlap=200  # Maintain context
            )

            if success:
                success_count += 1
                logger.info(f"✅ Successfully ingested: {pdf_path.name}")
            else:
                fail_count += 1
                logger.warning(f"⚠️  Failed to ingest: {pdf_path.name}")

        except Exception as e:
            fail_count += 1
            logger.error(f"❌ Error ingesting {pdf_path.name}: {str(e)}")
            continue

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"INGESTION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Successful: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")
    logger.info(f"📊 Total items ingested: {pipeline.ingested_count}")

    # Get collection info
    info = vector_service.get_collection_info(args.collection)
    if info:
        logger.info(f"\nCollection '{args.collection}' now contains:")
        logger.info(f"  - {info['points_count']} vectors")
        logger.info(f"  - Vector size: {info['config']['vector_size']}")
        logger.info(f"  - Distance metric: {info['config']['distance']}")

    logger.info(f"\n🎉 Books are now ready for genius-level research!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
