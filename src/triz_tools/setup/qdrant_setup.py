#!/usr/bin/env python3
"""
Qdrant Collection Setup for TRIZ Knowledge Base (T046)
Creates and configures vector database collections.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.triz_tools.services.vector_service import get_vector_service
from qdrant_client.models import Distance

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Collection configurations
COLLECTIONS = {
    "triz_principles": {
        "vector_size": 768,  # nomic-embed-text dimension
        "distance": Distance.COSINE,
        "description": "TRIZ 40 inventive principles with embeddings",
        "fields": [
            "principle_id",
            "principle_number", 
            "principle_name",
            "description",
            "sub_principles",
            "examples",
            "domains",
            "usage_frequency",
            "innovation_level"
        ]
    },
    "triz_contradictions": {
        "vector_size": 768,
        "distance": Distance.COSINE,
        "description": "Contradiction patterns and resolutions",
        "fields": [
            "contradiction_id",
            "improving_parameter",
            "worsening_parameter",
            "recommended_principles",
            "confidence_score",
            "application_count"
        ]
    },
    "solution_concepts": {
        "vector_size": 768,
        "distance": Distance.COSINE,
        "description": "Generated solution concepts from sessions",
        "fields": [
            "concept_id",
            "session_id",
            "concept_title",
            "description",
            "applied_principles",
            "feasibility_score",
            "innovation_level",
            "timestamp"
        ]
    },
    "problem_sessions": {
        "vector_size": 768,
        "distance": Distance.COSINE,
        "description": "Problem statements from user sessions",
        "fields": [
            "session_id",
            "problem_statement",
            "ideal_final_result",
            "contradictions",
            "stage",
            "timestamp"
        ]
    },
    "materials_database": {
        "vector_size": 512,  # Smaller for material properties
        "distance": Distance.EUCLID,  # Better for numeric properties
        "description": "Engineering materials with properties",
        "fields": [
            "material_id",
            "material_name",
            "material_type",
            "density",
            "strength",
            "cost_index",
            "applications",
            "advantages",
            "disadvantages"
        ]
    }
}


def setup_collections(
    host: str = "localhost",
    port: int = 6333,
    recreate: bool = False
) -> Dict[str, bool]:
    """
    Setup all Qdrant collections for TRIZ knowledge base.
    
    Args:
        host: Qdrant host
        port: Qdrant port
        recreate: Delete and recreate existing collections
    
    Returns:
        Dictionary with collection names and success status
    """
    results = {}
    
    # Get vector service
    vector_service = get_vector_service(host=host, port=port)
    
    if not vector_service.is_available():
        logger.error("Qdrant service not available. Is it running?")
        logger.info("Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
        return {name: False for name in COLLECTIONS}
    
    logger.info(f"Connected to Qdrant at {host}:{port}")
    
    # Process each collection
    for collection_name, config in COLLECTIONS.items():
        logger.info(f"\nProcessing collection: {collection_name}")
        logger.info(f"  Description: {config['description']}")
        logger.info(f"  Vector size: {config['vector_size']}")
        logger.info(f"  Distance: {config['distance'].value}")
        
        try:
            # Delete if recreate flag is set
            if recreate:
                logger.info(f"  Deleting existing collection...")
                vector_service.delete_collection(collection_name)
            
            # Create collection
            success = vector_service.create_collection(
                collection_name=collection_name,
                vector_size=config["vector_size"],
                distance=config["distance"],
                on_disk=False  # Keep in RAM for performance
            )
            
            if success:
                # Verify creation
                info = vector_service.get_collection_info(collection_name)
                if info:
                    logger.info(f"  ✅ Collection created successfully")
                    logger.info(f"     Status: {info['status']}")
                    logger.info(f"     Vector size: {info['config']['vector_size']}")
                    results[collection_name] = True
                else:
                    logger.error(f"  ❌ Failed to verify collection")
                    results[collection_name] = False
            else:
                logger.error(f"  ❌ Failed to create collection")
                results[collection_name] = False
                
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            results[collection_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Collection Setup Summary:")
    for name, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        logger.info(f"  {name}: {status}")
    
    total = len(results)
    successful = sum(1 for s in results.values() if s)
    logger.info(f"\nTotal: {successful}/{total} collections ready")
    
    return results


def verify_setup(host: str = "localhost", port: int = 6333) -> bool:
    """
    Verify that all collections are properly set up.
    
    Args:
        host: Qdrant host
        port: Qdrant port
    
    Returns:
        True if all collections exist and are configured correctly
    """
    vector_service = get_vector_service(host=host, port=port)
    
    if not vector_service.is_available():
        logger.error("Qdrant service not available")
        return False
    
    all_valid = True
    logger.info("Verifying Qdrant collections...")
    
    for collection_name, expected_config in COLLECTIONS.items():
        info = vector_service.get_collection_info(collection_name)
        
        if info is None:
            logger.error(f"  ❌ {collection_name}: Not found")
            all_valid = False
        elif info['config']['vector_size'] != expected_config['vector_size']:
            logger.error(
                f"  ❌ {collection_name}: Wrong vector size "
                f"(expected {expected_config['vector_size']}, got {info['config']['vector_size']})"
            )
            all_valid = False
        else:
            logger.info(
                f"  ✅ {collection_name}: OK "
                f"(vectors: {info['vectors_count']}, status: {info['status']})"
            )
    
    return all_valid


def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Qdrant collections for TRIZ")
    parser.add_argument("--host", default="localhost", help="Qdrant host")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant port")
    parser.add_argument("--recreate", action="store_true", help="Recreate existing collections")
    parser.add_argument("--verify", action="store_true", help="Only verify existing setup")
    
    args = parser.parse_args()
    
    if args.verify:
        # Just verify
        is_valid = verify_setup(host=args.host, port=args.port)
        sys.exit(0 if is_valid else 1)
    else:
        # Setup collections
        results = setup_collections(
            host=args.host,
            port=args.port,
            recreate=args.recreate
        )
        
        # Exit with error if any failed
        if all(results.values()):
            logger.info("\n✅ All collections ready for use!")
            sys.exit(0)
        else:
            logger.error("\n❌ Some collections failed to setup")
            sys.exit(1)


if __name__ == "__main__":
    main()