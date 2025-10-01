"""
Vector Database Service for TRIZ Knowledge Base (T028)
Manages Qdrant vector database operations for semantic search.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    UpdateStatus,
)
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Vector search result"""
    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None


class VectorService:
    """Service for managing vector database operations"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        timeout: int = 30,
        prefer_grpc: bool = False
    ):
        """
        Initialize vector service with Qdrant client.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            timeout: Operation timeout in seconds
            prefer_grpc: Use gRPC instead of HTTP
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        
        try:
            self.client = QdrantClient(
                host=host,
                port=port,
                timeout=timeout,
                prefer_grpc=prefer_grpc
            )
            self._initialized = self._check_connection()
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            self._initialized = False
            self.client = None
    
    def _check_connection(self) -> bool:
        """Check if Qdrant connection is working"""
        try:
            # Try to get collection info (will fail if not connected)
            self.client.get_collections()
            return True
        except Exception as e:
            logger.warning(f"Qdrant connection check failed: {str(e)}")
            return False
    
    def is_available(self) -> bool:
        """Check if vector service is available"""
        return self._initialized and self.client is not None
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
        on_disk: bool = False
    ) -> bool:
        """
        Create a new collection in Qdrant.
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors
            distance: Distance metric (COSINE, EUCLID, DOT)
            on_disk: Store vectors on disk instead of RAM
        
        Returns:
            True if successful
        """
        if not self.is_available():
            logger.error("Vector service not available")
            return False
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if exists:
                logger.info(f"Collection '{collection_name}' already exists")
                return True
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance,
                    on_disk=on_disk
                )
            )
            
            logger.info(f"Created collection '{collection_name}' with vector size {vector_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        if not self.is_available():
            return False
        
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False
    
    def insert_vectors(
        self,
        collection_name: str,
        vectors: List[np.ndarray],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> bool:
        """
        Insert vectors with payloads into collection.
        
        Args:
            collection_name: Target collection
            vectors: List of numpy arrays
            payloads: List of metadata dictionaries
            ids: Optional list of IDs (auto-generated if None)
            batch_size: Number of vectors per batch
        
        Returns:
            True if successful
        """
        if not self.is_available():
            return False
        
        if len(vectors) != len(payloads):
            logger.error("Vectors and payloads must have same length")
            return False
        
        try:
            points = []
            for i, (vector, payload) in enumerate(zip(vectors, payloads)):
                point_id = ids[i] if ids else i
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector.tolist() if isinstance(vector, np.ndarray) else vector,
                        payload=payload
                    )
                )
                
                # Upload in batches
                if len(points) >= batch_size:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
                    points = []
            
            # Upload remaining points
            if points:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
            
            logger.info(f"Inserted {len(vectors)} vectors into '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert vectors: {str(e)}")
            return False
    
    def search(
        self,
        collection_name: str,
        query_vector: np.ndarray,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            collection_name: Collection to search
            query_vector: Query vector
            limit: Maximum results to return
            score_threshold: Minimum similarity score
            filter_conditions: Optional filter conditions
        
        Returns:
            List of search results
        """
        if not self.is_available():
            return []
        
        try:
            # Build filter if conditions provided
            search_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                search_filter = Filter(must=conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector,
                limit=limit,
                query_filter=search_filter,
                score_threshold=score_threshold
            )
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_results.append(
                    SearchResult(
                        id=str(result.id),
                        score=result.score,
                        payload=result.payload or {}
                    )
                )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def get_vector(
        self,
        collection_name: str,
        vector_id: str
    ) -> Optional[SearchResult]:
        """
        Retrieve a specific vector by ID.
        
        Args:
            collection_name: Collection name
            vector_id: Vector ID
        
        Returns:
            SearchResult or None if not found
        """
        if not self.is_available():
            return None
        
        try:
            results = self.client.retrieve(
                collection_name=collection_name,
                ids=[vector_id],
                with_vectors=True,
                with_payload=True
            )
            
            if results:
                result = results[0]
                return SearchResult(
                    id=str(result.id),
                    score=1.0,  # Perfect match for direct retrieval
                    payload=result.payload or {},
                    vector=result.vector
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve vector: {str(e)}")
            return None
    
    def update_payload(
        self,
        collection_name: str,
        vector_id: str,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Update payload for a vector.
        
        Args:
            collection_name: Collection name
            vector_id: Vector ID
            payload: New payload data
        
        Returns:
            True if successful
        """
        if not self.is_available():
            return False
        
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=payload,
                points=[vector_id]
            )
            logger.info(f"Updated payload for vector {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update payload: {str(e)}")
            return False
    
    def delete_vectors(
        self,
        collection_name: str,
        vector_ids: List[str]
    ) -> bool:
        """
        Delete vectors by IDs.
        
        Args:
            collection_name: Collection name
            vector_ids: List of vector IDs to delete
        
        Returns:
            True if successful
        """
        if not self.is_available():
            return False
        
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=vector_ids
            )
            logger.info(f"Deleted {len(vector_ids)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {str(e)}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Collection name
        
        Returns:
            Dictionary with collection info or None
        """
        if not self.is_available():
            return None
        
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return None


# Singleton instance
_vector_service: Optional[VectorService] = None


def get_vector_service(
    host: str = "localhost",
    port: int = 6333,
    reset: bool = False
) -> VectorService:
    """
    Get or create vector service singleton.
    
    Args:
        host: Qdrant host
        port: Qdrant port
        reset: Force create new instance
    
    Returns:
        VectorService instance
    """
    global _vector_service
    
    if reset or _vector_service is None:
        _vector_service = VectorService(host=host, port=port)
    
    return _vector_service