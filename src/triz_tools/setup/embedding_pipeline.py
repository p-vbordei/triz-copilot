#!/usr/bin/env python3
"""
Vector Embedding Generation Pipeline (T050)
Generates embeddings for all TRIZ knowledge base content.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import argparse
import sys
import time
import numpy as np
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from triz_tools.services.embedding_service import get_embedding_service
    from triz_tools.services.vector_service import get_vector_service
    from triz_tools.knowledge_base import get_knowledge_base
    from triz_tools.contradiction_matrix import get_matrix_lookup
    from triz_tools.services.materials_service import get_materials_service
except ImportError:
    from ..services.embedding_service import get_embedding_service
    from ..services.vector_service import get_vector_service
    from ..knowledge_base import get_knowledge_base
    from ..contradiction_matrix import get_matrix_lookup
    from ..services.materials_service import get_materials_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmbeddingStats:
    """Statistics for embedding generation"""
    total_items: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    time_elapsed: float = 0.0
    
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_items == 0:
            return 0.0
        return self.successful / self.total_items
    
    def average_time(self) -> float:
        """Calculate average time per item"""
        if self.successful == 0:
            return 0.0
        return self.time_elapsed / self.successful


class EmbeddingPipeline:
    """Pipeline for generating embeddings for all knowledge"""
    
    def __init__(self, batch_size: int = 10):
        """
        Initialize embedding pipeline.
        
        Args:
            batch_size: Number of items to process in batch
        """
        self.embedding_service = get_embedding_service()
        self.vector_service = get_vector_service()
        self.batch_size = batch_size
        
        # Collections
        self.collections = {
            "principles": 768,  # nomic-embed-text dimension
            "materials": 768,
            "contradictions": 768,
            "solutions": 768,
            "knowledge": 768
        }
        
        # Statistics
        self.stats = {
            "principles": EmbeddingStats(),
            "materials": EmbeddingStats(),
            "contradictions": EmbeddingStats(),
            "knowledge": EmbeddingStats()
        }
        
        logger.info(f"Embedding pipeline initialized with batch size {batch_size}")
    
    def initialize_collections(self) -> bool:
        """
        Initialize vector collections.
        
        Returns:
            True if successful
        """
        for collection_name, vector_size in self.collections.items():
            try:
                self.vector_service.create_collection(
                    collection_name=collection_name,
                    vector_size=vector_size
                )
                logger.info(f"Created collection: {collection_name}")
            except Exception as e:
                logger.debug(f"Collection {collection_name} may already exist: {str(e)}")
        
        return True
    
    def generate_principle_embeddings(self) -> EmbeddingStats:
        """
        Generate embeddings for TRIZ principles.
        
        Returns:
            Generation statistics
        """
        logger.info("Generating principle embeddings...")
        
        stats = EmbeddingStats()
        start_time = time.time()
        
        kb = get_knowledge_base()
        
        for principle_id in range(1, 41):
            stats.total_items += 1
            
            try:
                principle = kb.get_principle(principle_id)
                if not principle:
                    stats.skipped += 1
                    continue
                
                # Create text representation
                text = self._principle_to_text(principle_id, principle)
                
                # Generate embedding
                embedding = self.embedding_service.generate_embedding(text)
                
                if embedding is not None:
                    # Store in vector DB
                    self.vector_service.add_vectors(
                        collection_name="principles",
                        vectors=[embedding],
                        payloads=[{
                            "principle_id": principle_id,
                            "name": principle.get("name", f"Principle {principle_id}"),
                            "description": principle.get("description", ""),
                            "examples": principle.get("examples", [])[:3],
                            "type": "principle"
                        }]
                    )
                    
                    stats.successful += 1
                    logger.debug(f"Generated embedding for principle {principle_id}")
                else:
                    stats.failed += 1
                    logger.warning(f"Failed to generate embedding for principle {principle_id}")
                    
            except Exception as e:
                stats.failed += 1
                logger.error(f"Error processing principle {principle_id}: {str(e)}")
        
        stats.time_elapsed = time.time() - start_time
        self.stats["principles"] = stats
        
        logger.info(f"Principle embeddings: {stats.successful}/{stats.total_items} successful")
        return stats
    
    def generate_material_embeddings(self) -> EmbeddingStats:
        """
        Generate embeddings for materials.
        
        Returns:
            Generation statistics
        """
        logger.info("Generating material embeddings...")
        
        stats = EmbeddingStats()
        start_time = time.time()
        
        materials_service = get_materials_service()
        
        for material in materials_service.materials.values():
            stats.total_items += 1
            
            try:
                # Create text representation
                text = self._material_to_text(material)
                
                # Generate embedding
                embedding = self.embedding_service.generate_embedding(text)
                
                if embedding is not None:
                    # Store in vector DB
                    self.vector_service.add_vectors(
                        collection_name="materials",
                        vectors=[embedding],
                        payloads=[{
                            "material_id": material.material_id,
                            "name": material.name,
                            "category": material.category,
                            "properties": material.properties,
                            "advantages": material.advantages[:3],
                            "applications": material.applications[:3],
                            "type": "material"
                        }]
                    )
                    
                    stats.successful += 1
                    logger.debug(f"Generated embedding for {material.name}")
                else:
                    stats.failed += 1
                    logger.warning(f"Failed to generate embedding for {material.name}")
                    
            except Exception as e:
                stats.failed += 1
                logger.error(f"Error processing material {material.material_id}: {str(e)}")
        
        stats.time_elapsed = time.time() - start_time
        self.stats["materials"] = stats
        
        logger.info(f"Material embeddings: {stats.successful}/{stats.total_items} successful")
        return stats
    
    def generate_contradiction_embeddings(self) -> EmbeddingStats:
        """
        Generate embeddings for contradictions.
        
        Returns:
            Generation statistics
        """
        logger.info("Generating contradiction embeddings...")
        
        stats = EmbeddingStats()
        start_time = time.time()
        
        matrix_lookup = get_matrix_lookup()
        
        for key, result in matrix_lookup.matrix.matrix.items():
            stats.total_items += 1
            
            try:
                improving, worsening = key
                
                # Get parameter names
                imp_param = matrix_lookup.matrix.get_parameter(improving)
                wor_param = matrix_lookup.matrix.get_parameter(worsening)
                
                # Create text representation
                text = self._contradiction_to_text(
                    improving, worsening,
                    imp_param, wor_param,
                    result.recommended_principles
                )
                
                # Generate embedding
                embedding = self.embedding_service.generate_embedding(text)
                
                if embedding is not None:
                    # Store in vector DB
                    self.vector_service.add_vectors(
                        collection_name="contradictions",
                        vectors=[embedding],
                        payloads=[{
                            "improving": improving,
                            "worsening": worsening,
                            "improving_name": imp_param.parameter_name if imp_param else f"Parameter {improving}",
                            "worsening_name": wor_param.parameter_name if wor_param else f"Parameter {worsening}",
                            "principles": result.recommended_principles,
                            "confidence": result.confidence_score,
                            "type": "contradiction"
                        }]
                    )
                    
                    stats.successful += 1
                    logger.debug(f"Generated embedding for contradiction {improving}-{worsening}")
                else:
                    stats.failed += 1
                    logger.warning(f"Failed to generate embedding for contradiction {improving}-{worsening}")
                    
            except Exception as e:
                stats.failed += 1
                logger.error(f"Error processing contradiction {key}: {str(e)}")
        
        stats.time_elapsed = time.time() - start_time
        self.stats["contradictions"] = stats
        
        logger.info(f"Contradiction embeddings: {stats.successful}/{stats.total_items} successful")
        return stats
    
    def generate_knowledge_embeddings(
        self,
        knowledge_dir: Optional[Path] = None
    ) -> EmbeddingStats:
        """
        Generate embeddings for knowledge base files.
        
        Args:
            knowledge_dir: Directory with knowledge files
        
        Returns:
            Generation statistics
        """
        logger.info("Generating knowledge embeddings...")
        
        stats = EmbeddingStats()
        start_time = time.time()
        
        if knowledge_dir is None:
            knowledge_dir = Path(__file__).parent.parent / "data"
        
        if not knowledge_dir.exists():
            logger.warning(f"Knowledge directory not found: {knowledge_dir}")
            return stats
        
        # Process text files
        for text_file in knowledge_dir.glob("*.txt"):
            stats.total_items += 1
            
            try:
                with open(text_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Split into chunks if too long
                chunks = self._split_text(content, max_length=1000)
                
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    embedding = self.embedding_service.generate_embedding(chunk)
                    
                    if embedding is not None:
                        # Store in vector DB
                        self.vector_service.add_vectors(
                            collection_name="knowledge",
                            vectors=[embedding],
                            payloads=[{
                                "source": text_file.name,
                                "chunk_index": i,
                                "content": chunk[:500],  # Store preview
                                "type": "knowledge"
                            }]
                        )
                        
                        stats.successful += 1
                        logger.debug(f"Generated embedding for {text_file.name} chunk {i}")
                    else:
                        stats.failed += 1
                        
            except Exception as e:
                stats.failed += 1
                logger.error(f"Error processing {text_file}: {str(e)}")
        
        stats.time_elapsed = time.time() - start_time
        self.stats["knowledge"] = stats
        
        logger.info(f"Knowledge embeddings: {stats.successful}/{stats.total_items} successful")
        return stats
    
    def _principle_to_text(self, principle_id: int, principle: Dict[str, Any]) -> str:
        """Convert principle to text for embedding"""
        parts = [
            f"TRIZ Principle {principle_id}",
            principle.get("name", f"Principle {principle_id}"),
            principle.get("description", "")
        ]
        
        examples = principle.get("examples", [])
        if examples:
            parts.append(f"Examples: {', '.join(examples[:3])}")
        
        return " | ".join(filter(None, parts))
    
    def _material_to_text(self, material) -> str:
        """Convert material to text for embedding"""
        parts = [
            f"Material: {material.name}",
            f"Category: {material.category}"
        ]
        
        # Add key properties
        for prop, value in list(material.properties.items())[:5]:
            parts.append(f"{prop}: {value}")
        
        if material.advantages:
            parts.append(f"Advantages: {', '.join(material.advantages[:3])}")
        
        if material.applications:
            parts.append(f"Applications: {', '.join(material.applications[:3])}")
        
        return " | ".join(parts)
    
    def _contradiction_to_text(
        self,
        improving: int,
        worsening: int,
        imp_param,
        wor_param,
        principles: List[int]
    ) -> str:
        """Convert contradiction to text for embedding"""
        imp_name = imp_param.parameter_name if imp_param else f"Parameter {improving}"
        wor_name = wor_param.parameter_name if wor_param else f"Parameter {worsening}"
        
        parts = [
            f"Contradiction: Improve {imp_name} while {wor_name} worsens",
            f"Recommended principles: {', '.join(map(str, principles))}"
        ]
        
        if imp_param and imp_param.description:
            parts.append(f"Improving: {imp_param.description}")
        
        if wor_param and wor_param.description:
            parts.append(f"Worsening: {wor_param.description}")
        
        return " | ".join(parts)
    
    def _split_text(self, text: str, max_length: int = 1000) -> List[str]:
        """Split text into chunks"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split(". ")
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def run_full_pipeline(
        self,
        knowledge_dir: Optional[Path] = None
    ) -> Dict[str, EmbeddingStats]:
        """
        Run complete embedding generation pipeline.
        
        Args:
            knowledge_dir: Directory with knowledge files
        
        Returns:
            Statistics for all collections
        """
        logger.info("Starting full embedding pipeline...")
        
        # Initialize collections
        self.initialize_collections()
        
        # Generate embeddings for each type
        self.generate_principle_embeddings()
        self.generate_material_embeddings()
        self.generate_contradiction_embeddings()
        self.generate_knowledge_embeddings(knowledge_dir)
        
        # Print summary
        self.print_summary()
        
        return self.stats
    
    def print_summary(self):
        """Print generation summary"""
        print("\n" + "="*60)
        print("EMBEDDING GENERATION SUMMARY")
        print("="*60)
        
        total_items = 0
        total_successful = 0
        total_time = 0.0
        
        for collection, stats in self.stats.items():
            if stats.total_items > 0:
                print(f"\n{collection.upper()}:")
                print(f"  Total items: {stats.total_items}")
                print(f"  Successful: {stats.successful}")
                print(f"  Failed: {stats.failed}")
                print(f"  Skipped: {stats.skipped}")
                print(f"  Success rate: {stats.success_rate():.1%}")
                print(f"  Time elapsed: {stats.time_elapsed:.2f}s")
                print(f"  Avg time/item: {stats.average_time():.3f}s")
                
                total_items += stats.total_items
                total_successful += stats.successful
                total_time += stats.time_elapsed
        
        print("\n" + "-"*60)
        print("TOTAL:")
        print(f"  Items processed: {total_items}")
        print(f"  Successful: {total_successful}")
        print(f"  Overall success rate: {total_successful/total_items:.1%}" if total_items > 0 else "N/A")
        print(f"  Total time: {total_time:.2f}s")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate embeddings for TRIZ knowledge")
    parser.add_argument(
        "--principles",
        action="store_true",
        help="Generate principle embeddings"
    )
    parser.add_argument(
        "--materials",
        action="store_true",
        help="Generate material embeddings"
    )
    parser.add_argument(
        "--contradictions",
        action="store_true",
        help="Generate contradiction embeddings"
    )
    parser.add_argument(
        "--knowledge",
        action="store_true",
        help="Generate knowledge embeddings"
    )
    parser.add_argument(
        "--knowledge-dir",
        type=Path,
        help="Directory with knowledge files"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all embeddings"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for processing"
    )
    
    args = parser.parse_args()
    
    pipeline = EmbeddingPipeline(batch_size=args.batch_size)
    
    # Initialize collections
    pipeline.initialize_collections()
    
    # Run requested generations
    if args.all:
        pipeline.run_full_pipeline(args.knowledge_dir)
    else:
        if args.principles:
            pipeline.generate_principle_embeddings()
        
        if args.materials:
            pipeline.generate_material_embeddings()
        
        if args.contradictions:
            pipeline.generate_contradiction_embeddings()
        
        if args.knowledge:
            pipeline.generate_knowledge_embeddings(args.knowledge_dir)
        
        # Print summary if anything was generated
        if any([args.principles, args.materials, args.contradictions, args.knowledge]):
            pipeline.print_summary()
        else:
            print("No embeddings generated. Use --all or specify collections.")


if __name__ == "__main__":
    main()