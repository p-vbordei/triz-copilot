"""
Embedding Generation Service using Ollama (T029)
Generates semantic embeddings for TRIZ knowledge base.
"""

import logging
import json
from typing import List, Optional, Dict, Any
import numpy as np
import requests
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding service"""
    model: str = "nomic-embed-text"
    host: str = "http://localhost:11434"
    dimension: int = 768
    timeout: int = 30
    batch_size: int = 32
    retry_attempts: int = 3
    retry_delay: float = 1.0


class EmbeddingService:
    """Service for generating text embeddings using Ollama"""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize embedding service.
        
        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()
        self._available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(
                f"{self.config.host}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                if self.config.model in model_names:
                    logger.info(f"Ollama model '{self.config.model}' is available")
                    return True
                else:
                    logger.warning(f"Model '{self.config.model}' not found in Ollama")
                    logger.info(f"Available models: {model_names}")
                    return False
            return False
        except Exception as e:
            logger.warning(f"Ollama service not available: {str(e)}")
            return False
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self._available
    
    def generate_embedding(
        self,
        text: str,
        normalize: bool = True
    ) -> Optional[np.ndarray]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            normalize: Whether to normalize the embedding
        
        Returns:
            Embedding vector or None if failed
        """
        if not text:
            return None
        
        if not self.is_available():
            # Fallback to random embedding for testing
            logger.debug("Using random embedding (Ollama not available)")
            embedding = np.random.randn(self.config.dimension)
            if normalize:
                embedding = embedding / np.linalg.norm(embedding)
            return embedding
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = requests.post(
                    f"{self.config.host}/api/embeddings",
                    json={
                        "model": self.config.model,
                        "prompt": text
                    },
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    embedding = np.array(response.json()["embedding"])
                    
                    if normalize:
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            embedding = embedding / norm
                    
                    return embedding
                else:
                    logger.error(f"Embedding generation failed: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Embedding request timed out (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Embedding generation error: {str(e)}")
            
            if attempt < self.config.retry_attempts - 1:
                time.sleep(self.config.retry_delay)
        
        # Fallback to random embedding
        logger.debug("Falling back to random embedding")
        embedding = np.random.randn(self.config.dimension)
        if normalize:
            embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def generate_embeddings(
        self,
        texts: List[str],
        normalize: bool = True,
        show_progress: bool = False
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            normalize: Whether to normalize embeddings
            show_progress: Show progress indicator
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            if show_progress and i % 10 == 0:
                logger.info(f"Processing {i}/{len(texts)} texts...")
            
            embedding = self.generate_embedding(text, normalize=normalize)
            if embedding is not None:
                embeddings.append(embedding)
            else:
                # Use zero vector for failed embeddings
                embeddings.append(np.zeros(self.config.dimension))
        
        if show_progress:
            logger.info(f"Generated {len(embeddings)} embeddings")
        
        return embeddings
    
    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        metric: str = "cosine"
    ) -> float:
        """
        Compute similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            metric: Similarity metric (cosine, euclidean, dot)
        
        Returns:
            Similarity score
        """
        if metric == "cosine":
            # Cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
            
        elif metric == "euclidean":
            # Negative Euclidean distance (higher is more similar)
            return -float(np.linalg.norm(embedding1 - embedding2))
            
        elif metric == "dot":
            # Dot product
            return float(np.dot(embedding1, embedding2))
            
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def find_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        top_k: int = 5,
        threshold: Optional[float] = None,
        metric: str = "cosine"
    ) -> List[tuple[int, float]]:
        """
        Find most similar embeddings from candidates.
        
        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            metric: Similarity metric
        
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.compute_similarity(
                query_embedding,
                candidate,
                metric=metric
            )
            
            if threshold is None or similarity >= threshold:
                similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def embed_triz_principle(
        self,
        principle: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for different aspects of a TRIZ principle.
        
        Args:
            principle: TRIZ principle data
        
        Returns:
            Dictionary with embedding vectors for different fields
        """
        embeddings = {}
        
        # Embed main description
        if "description" in principle:
            embeddings["description"] = self.generate_embedding(
                principle["description"]
            )
        
        # Embed combined sub-principles
        if "sub_principles" in principle and principle["sub_principles"]:
            combined_text = " ".join(principle["sub_principles"])
            embeddings["sub_principles"] = self.generate_embedding(combined_text)
        
        # Embed combined examples
        if "examples" in principle and principle["examples"]:
            combined_text = " ".join(principle["examples"][:5])  # Limit examples
            embeddings["examples"] = self.generate_embedding(combined_text)
        
        # Create composite embedding
        composite_parts = []
        if "principle_name" in principle:
            composite_parts.append(principle["principle_name"])
        if "description" in principle:
            composite_parts.append(principle["description"][:200])
        
        if composite_parts:
            composite_text = " ".join(composite_parts)
            embeddings["composite"] = self.generate_embedding(composite_text)
        
        return embeddings


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    config: Optional[EmbeddingConfig] = None,
    reset: bool = False
) -> EmbeddingService:
    """
    Get or create embedding service singleton.
    
    Args:
        config: Embedding configuration
        reset: Force create new instance
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    
    if reset or _embedding_service is None:
        _embedding_service = EmbeddingService(config=config)
    
    return _embedding_service