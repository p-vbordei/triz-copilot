"""
File-based Vector Service Fallback
Provides vector storage using local files when Qdrant is not available.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pickle

from ..embeddings import compute_similarity

logger = logging.getLogger(__name__)


class FileVectorService:
    """File-based fallback for vector storage"""
    
    def __init__(self, storage_dir: Path = None):
        """
        Initialize file-based vector service.
        
        Args:
            storage_dir: Directory for storing vectors
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".triz_copilot" / "vectors"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for loaded collections
        self._collections = {}
        self._load_collections()
        
        logger.info(f"File-based vector service initialized at {self.storage_dir}")
    
    def _load_collections(self):
        """Load existing collections from disk"""
        for collection_file in self.storage_dir.glob("*.json"):
            collection_name = collection_file.stem
            try:
                with open(collection_file, "r") as f:
                    self._collections[collection_name] = json.load(f)
                logger.info(f"Loaded collection '{collection_name}' with {len(self._collections[collection_name]['items'])} items")
            except Exception as e:
                logger.error(f"Failed to load collection {collection_name}: {str(e)}")
    
    def _save_collection(self, collection_name: str):
        """Save collection to disk"""
        if collection_name in self._collections:
            collection_file = self.storage_dir / f"{collection_name}.json"
            
            # Convert numpy arrays to lists for JSON serialization
            collection_data = self._collections[collection_name].copy()
            for item in collection_data.get("items", []):
                if "vector" in item and isinstance(item["vector"], np.ndarray):
                    item["vector"] = item["vector"].tolist()
            
            with open(collection_file, "w") as f:
                json.dump(collection_data, f, indent=2)
    
    def is_available(self) -> bool:
        """Check if service is available"""
        return True  # Always available
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        **kwargs
    ) -> bool:
        """Create a new collection"""
        if collection_name not in self._collections:
            self._collections[collection_name] = {
                "name": collection_name,
                "vector_size": vector_size,
                "items": [],
                "metadata": kwargs
            }
            self._save_collection(collection_name)
            logger.info(f"Created file-based collection '{collection_name}'")
        return True
    
    def insert_vectors(
        self,
        collection_name: str,
        vectors: List[np.ndarray],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        **kwargs
    ) -> bool:
        """Insert vectors into collection"""
        if collection_name not in self._collections:
            # Auto-create collection
            vector_size = len(vectors[0]) if vectors else 768
            self.create_collection(collection_name, vector_size)
        
        collection = self._collections[collection_name]
        
        for i, (vector, payload) in enumerate(zip(vectors, payloads)):
            item_id = ids[i] if ids else f"item_{len(collection['items'])}"
            
            item = {
                "id": item_id,
                "vector": vector.tolist() if isinstance(vector, np.ndarray) else vector,
                "payload": payload
            }
            
            # Check if ID exists and update
            existing_idx = None
            for idx, existing_item in enumerate(collection["items"]):
                if existing_item["id"] == item_id:
                    existing_idx = idx
                    break
            
            if existing_idx is not None:
                collection["items"][existing_idx] = item
            else:
                collection["items"].append(item)
        
        self._save_collection(collection_name)
        logger.info(f"Inserted {len(vectors)} vectors into '{collection_name}'")
        return True
    
    def search(
        self,
        collection_name: str,
        query_vector: np.ndarray,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        if collection_name not in self._collections:
            logger.warning(f"Collection '{collection_name}' not found")
            return []
        
        collection = self._collections[collection_name]
        results = []
        
        # Convert query vector to numpy if needed
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector)
        
        # Calculate similarities
        for item in collection["items"]:
            # Apply filters if provided
            if filter_conditions:
                match = all(
                    item["payload"].get(key) == value
                    for key, value in filter_conditions.items()
                )
                if not match:
                    continue
            
            # Calculate similarity
            item_vector = np.array(item["vector"])
            similarity = compute_similarity(query_vector, item_vector, metric="cosine")
            
            # Apply threshold
            if score_threshold is None or similarity >= score_threshold:
                results.append({
                    "id": item["id"],
                    "score": similarity,
                    "payload": item["payload"]
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def get_vector(
        self,
        collection_name: str,
        vector_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific vector by ID"""
        if collection_name not in self._collections:
            return None
        
        collection = self._collections[collection_name]
        
        for item in collection["items"]:
            if item["id"] == vector_id:
                return {
                    "id": item["id"],
                    "score": 1.0,
                    "payload": item["payload"],
                    "vector": item["vector"]
                }
        
        return None
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get collection information"""
        if collection_name not in self._collections:
            return None
        
        collection = self._collections[collection_name]
        
        return {
            "vectors_count": len(collection["items"]),
            "indexed_vectors_count": len(collection["items"]),
            "points_count": len(collection["items"]),
            "status": "ready",
            "config": {
                "vector_size": collection.get("vector_size", 768),
                "distance": "cosine"
            }
        }
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        if collection_name in self._collections:
            del self._collections[collection_name]
            
            collection_file = self.storage_dir / f"{collection_name}.json"
            if collection_file.exists():
                collection_file.unlink()
            
            logger.info(f"Deleted collection '{collection_name}'")
            return True
        
        return False


# Update the vector service to use file fallback when Qdrant is not available
def get_hybrid_vector_service(
    host: str = "localhost",
    port: int = 6333,
    fallback_dir: Optional[Path] = None
):
    """
    Get vector service with file-based fallback.
    
    Args:
        host: Qdrant host
        port: Qdrant port
        fallback_dir: Directory for file-based storage
    
    Returns:
        Vector service (Qdrant or file-based)
    """
    try:
        from .vector_service import VectorService
        
        # Try Qdrant first
        qdrant_service = VectorService(host=host, port=port)
        if qdrant_service.is_available():
            logger.info("Using Qdrant vector service")
            return qdrant_service
    except Exception as e:
        logger.debug(f"Qdrant not available: {str(e)}")
    
    # Fallback to file-based
    logger.info("Using file-based vector service (Qdrant not available)")
    return FileVectorService(storage_dir=fallback_dir)