"""
Ollama Embedding Client for TRIZ Tools (T036)
Simple interface for generating embeddings using Ollama.
"""

import logging
from typing import List, Optional, Union
import numpy as np

try:
    from .services.embedding_service import (
        get_embedding_service,
        EmbeddingConfig,
        EmbeddingService
    )
except ImportError:
    # For direct execution
    from services.embedding_service import (
        get_embedding_service,
        EmbeddingConfig,
        EmbeddingService
    )

logger = logging.getLogger(__name__)


def generate_embedding(
    text: str,
    model: str = "nomic-embed-text",
    normalize: bool = True
) -> Optional[np.ndarray]:
    """
    Generate embedding for a single text using Ollama.
    
    Args:
        text: Input text to embed
        model: Ollama model name
        normalize: Whether to normalize the embedding vector
    
    Returns:
        Embedding vector as numpy array or None if failed
    """
    if not text:
        logger.warning("Empty text provided for embedding")
        return None
    
    config = EmbeddingConfig(model=model)
    service = get_embedding_service(config=config)
    
    return service.generate_embedding(text, normalize=normalize)


def generate_embeddings_batch(
    texts: List[str],
    model: str = "nomic-embed-text",
    normalize: bool = True,
    show_progress: bool = False
) -> List[np.ndarray]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of texts to embed
        model: Ollama model name
        normalize: Whether to normalize embedding vectors
        show_progress: Show progress during generation
    
    Returns:
        List of embedding vectors
    """
    config = EmbeddingConfig(model=model)
    service = get_embedding_service(config=config)
    
    return service.generate_embeddings(
        texts,
        normalize=normalize,
        show_progress=show_progress
    )


def compute_similarity(
    text1: Union[str, np.ndarray],
    text2: Union[str, np.ndarray],
    model: str = "nomic-embed-text",
    metric: str = "cosine"
) -> float:
    """
    Compute similarity between two texts or embeddings.
    
    Args:
        text1: First text or embedding
        text2: Second text or embedding
        model: Ollama model name (if texts provided)
        metric: Similarity metric (cosine, euclidean, dot)
    
    Returns:
        Similarity score
    """
    service = get_embedding_service()
    
    # Convert texts to embeddings if needed
    if isinstance(text1, str):
        embedding1 = generate_embedding(text1, model=model)
    else:
        embedding1 = text1
    
    if isinstance(text2, str):
        embedding2 = generate_embedding(text2, model=model)
    else:
        embedding2 = text2
    
    if embedding1 is None or embedding2 is None:
        return 0.0
    
    return service.compute_similarity(embedding1, embedding2, metric=metric)


def find_most_similar(
    query: Union[str, np.ndarray],
    candidates: List[Union[str, np.ndarray]],
    model: str = "nomic-embed-text",
    top_k: int = 5,
    threshold: Optional[float] = None,
    metric: str = "cosine"
) -> List[tuple[int, float]]:
    """
    Find most similar items from candidates.
    
    Args:
        query: Query text or embedding
        candidates: List of candidate texts or embeddings
        model: Ollama model name (if texts provided)
        top_k: Number of top results
        threshold: Minimum similarity threshold
        metric: Similarity metric
    
    Returns:
        List of (index, similarity_score) tuples
    """
    service = get_embedding_service()
    
    # Convert query to embedding if needed
    if isinstance(query, str):
        query_embedding = generate_embedding(query, model=model)
    else:
        query_embedding = query
    
    if query_embedding is None:
        return []
    
    # Convert candidates to embeddings if needed
    candidate_embeddings = []
    for candidate in candidates:
        if isinstance(candidate, str):
            embedding = generate_embedding(candidate, model=model)
        else:
            embedding = candidate
        
        if embedding is not None:
            candidate_embeddings.append(embedding)
        else:
            # Use zero vector for failed embeddings
            candidate_embeddings.append(np.zeros(768))
    
    return service.find_similar(
        query_embedding,
        candidate_embeddings,
        top_k=top_k,
        threshold=threshold,
        metric=metric
    )


def embed_triz_content(
    content: dict,
    fields: List[str] = None
) -> dict:
    """
    Generate embeddings for TRIZ content fields.
    
    Args:
        content: Dictionary with TRIZ content
        fields: List of fields to embed (default: all text fields)
    
    Returns:
        Dictionary with original content plus embeddings
    """
    service = get_embedding_service()
    
    if fields is None:
        # Default fields to embed
        fields = ["description", "principle_name", "examples", "sub_principles"]
    
    result = content.copy()
    result["embeddings"] = {}
    
    for field in fields:
        if field in content:
            value = content[field]
            
            if isinstance(value, str):
                # Single text field
                embedding = service.generate_embedding(value)
                if embedding is not None:
                    result["embeddings"][field] = embedding
                    
            elif isinstance(value, list) and value:
                # List of texts - combine them
                combined = " ".join(str(v) for v in value[:10])  # Limit to 10 items
                embedding = service.generate_embedding(combined)
                if embedding is not None:
                    result["embeddings"][field] = embedding
    
    # Generate composite embedding from multiple fields
    composite_parts = []
    for field in ["principle_name", "description"]:
        if field in content:
            if isinstance(content[field], str):
                composite_parts.append(content[field][:500])
    
    if composite_parts:
        composite_text = " ".join(composite_parts)
        composite_embedding = service.generate_embedding(composite_text)
        if composite_embedding is not None:
            result["embeddings"]["composite"] = composite_embedding
    
    return result


def check_ollama_status() -> dict:
    """
    Check Ollama service status and available models.
    
    Returns:
        Dictionary with status information
    """
    service = get_embedding_service()
    
    status = {
        "available": service.is_available(),
        "model": service.config.model,
        "host": service.config.host,
        "dimension": service.config.dimension
    }
    
    if service.is_available():
        try:
            # Test embedding generation
            test_embedding = service.generate_embedding("test")
            status["test_successful"] = test_embedding is not None
            if test_embedding is not None:
                status["actual_dimension"] = len(test_embedding)
        except Exception as e:
            status["test_successful"] = False
            status["error"] = str(e)
    
    return status


# Convenience function for CLI testing
def test_embeddings():
    """Test embedding generation with sample texts"""
    print("Testing Ollama embeddings...")
    
    status = check_ollama_status()
    print(f"Status: {status}")
    
    if not status["available"]:
        print("⚠️ Ollama not available - using random embeddings")
    
    # Test single embedding
    text = "Segmentation principle: divide an object into independent parts"
    embedding = generate_embedding(text)
    
    if embedding is not None:
        print(f"✅ Generated embedding with dimension {len(embedding)}")
        print(f"   Norm: {np.linalg.norm(embedding):.4f}")
    else:
        print("❌ Failed to generate embedding")
    
    # Test similarity
    text1 = "Reduce weight while maintaining strength"
    text2 = "Make lighter but keep strong"
    text3 = "Increase temperature for faster reaction"
    
    sim12 = compute_similarity(text1, text2)
    sim13 = compute_similarity(text1, text3)
    
    print(f"\nSimilarity scores:")
    print(f"  '{text1[:30]}...' vs")
    print(f"  '{text2[:30]}...' = {sim12:.4f}")
    print(f"  '{text3[:30]}...' = {sim13:.4f}")
    
    # Test batch processing
    texts = [
        "Segmentation principle",
        "Asymmetry principle", 
        "Dynamics principle",
        "Composite materials"
    ]
    
    embeddings = generate_embeddings_batch(texts, show_progress=True)
    print(f"\n✅ Generated {len(embeddings)} embeddings in batch")
    
    return True


if __name__ == "__main__":
    # Run tests when executed directly
    logging.basicConfig(level=logging.INFO)
    test_embeddings()