#!/usr/bin/env python3
"""
Unit Tests: Embedding Generation (T057)
Tests for text embedding generation and caching.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import json
import time
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.embeddings import (
    EmbeddingClient,
    get_embedding_client,
    generate_embedding,
    batch_generate_embeddings,
    cosine_similarity,
    EmbeddingCache
)


class TestEmbeddingClient(unittest.TestCase):
    """Test EmbeddingClient functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = EmbeddingClient(
            model_name="test-model",
            cache_dir=Path(self.temp_dir)
        )
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_generate_embedding(self, mock_ollama):
        """Test generating single embedding"""
        # Mock Ollama response
        mock_ollama.embeddings.return_value = {
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        text = "Test text for embedding"
        embedding = self.client.generate(text)
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (5,))
        self.assertAlmostEqual(embedding[0], 0.1)
        
        # Verify Ollama was called correctly
        mock_ollama.embeddings.assert_called_once_with(
            model="test-model",
            prompt=text
        )
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_batch_generate(self, mock_ollama):
        """Test batch embedding generation"""
        # Mock responses
        embeddings_data = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ]
        
        mock_ollama.embeddings.side_effect = [
            {'embedding': emb} for emb in embeddings_data
        ]
        
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = self.client.batch_generate(texts)
        
        self.assertEqual(len(embeddings), 3)
        for i, embedding in enumerate(embeddings):
            self.assertIsInstance(embedding, np.ndarray)
            self.assertEqual(embedding.shape, (3,))
            np.testing.assert_array_almost_equal(
                embedding,
                np.array(embeddings_data[i])
            )
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_embedding_cache(self, mock_ollama):
        """Test embedding caching functionality"""
        mock_ollama.embeddings.return_value = {
            'embedding': [0.1, 0.2, 0.3]
        }
        
        text = "Cached text"
        
        # First call - should hit Ollama
        embedding1 = self.client.generate(text)
        self.assertEqual(mock_ollama.embeddings.call_count, 1)
        
        # Second call - should use cache
        embedding2 = self.client.generate(text)
        self.assertEqual(mock_ollama.embeddings.call_count, 1)  # No additional call
        
        # Embeddings should be identical
        np.testing.assert_array_equal(embedding1, embedding2)
    
    def test_empty_text_handling(self):
        """Test handling of empty text"""
        with self.assertRaises(ValueError):
            self.client.generate("")
        
        with self.assertRaises(ValueError):
            self.client.generate("   ")
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_long_text_handling(self, mock_ollama):
        """Test handling of long text"""
        mock_ollama.embeddings.return_value = {
            'embedding': [0.1] * 768
        }
        
        # Create very long text
        long_text = "word " * 10000  # Very long text
        
        embedding = self.client.generate(long_text)
        
        self.assertIsInstance(embedding, np.ndarray)
        # Should handle truncation internally
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_error_handling(self, mock_ollama):
        """Test error handling in embedding generation"""
        # Mock Ollama error
        mock_ollama.embeddings.side_effect = Exception("Ollama error")
        
        # Should use fallback
        embedding = self.client.generate("Test text")
        
        # Fallback should return consistent dimensions
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(len(embedding.shape), 1)
    
    def test_model_configuration(self):
        """Test model configuration"""
        client = EmbeddingClient(model_name="custom-model")
        
        self.assertEqual(client.model_name, "custom-model")
        self.assertEqual(client.embedding_dim, 768)  # Default dimension
        
        # With custom dimension
        client = EmbeddingClient(
            model_name="small-model",
            embedding_dim=384
        )
        
        self.assertEqual(client.embedding_dim, 384)


class TestEmbeddingCache(unittest.TestCase):
    """Test embedding cache functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = EmbeddingCache(cache_dir=Path(self.temp_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_set_and_get(self):
        """Test setting and getting cached embeddings"""
        key = "test_key"
        embedding = np.array([0.1, 0.2, 0.3])
        
        # Set cache
        self.cache.set(key, embedding)
        
        # Get from cache
        cached = self.cache.get(key)
        
        self.assertIsNotNone(cached)
        np.testing.assert_array_equal(cached, embedding)
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        result = self.cache.get("nonexistent_key")
        self.assertIsNone(result)
    
    def test_cache_persistence(self):
        """Test cache persistence across instances"""
        key = "persistent_key"
        embedding = np.array([0.4, 0.5, 0.6])
        
        # Set in first cache
        self.cache.set(key, embedding)
        
        # Create new cache instance
        new_cache = EmbeddingCache(cache_dir=Path(self.temp_dir))
        
        # Should retrieve from disk
        cached = new_cache.get(key)
        
        self.assertIsNotNone(cached)
        np.testing.assert_array_equal(cached, embedding)
    
    def test_cache_clear(self):
        """Test clearing cache"""
        # Add items to cache
        self.cache.set("key1", np.array([0.1]))
        self.cache.set("key2", np.array([0.2]))
        
        # Clear cache
        self.cache.clear()
        
        # Should be empty
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_cache_size_limit(self):
        """Test cache size limiting"""
        cache = EmbeddingCache(
            cache_dir=Path(self.temp_dir),
            max_size=3
        )
        
        # Add more than max_size items
        for i in range(5):
            cache.set(f"key{i}", np.array([float(i)]))
        
        # Only last max_size items should be in cache
        self.assertIsNone(cache.get("key0"))  # Evicted
        self.assertIsNone(cache.get("key1"))  # Evicted
        self.assertIsNotNone(cache.get("key2"))
        self.assertIsNotNone(cache.get("key3"))
        self.assertIsNotNone(cache.get("key4"))
    
    def test_cache_ttl(self):
        """Test cache time-to-live"""
        cache = EmbeddingCache(
            cache_dir=Path(self.temp_dir),
            ttl_seconds=0.1  # Very short TTL for testing
        )
        
        key = "ttl_key"
        embedding = np.array([0.7, 0.8])
        
        cache.set(key, embedding)
        
        # Should be in cache immediately
        self.assertIsNotNone(cache.get(key))
        
        # Wait for TTL to expire
        time.sleep(0.2)
        
        # Should be expired
        self.assertIsNone(cache.get(key))


class TestCosineSimilarity(unittest.TestCase):
    """Test cosine similarity calculation"""
    
    def test_cosine_similarity_identical(self):
        """Test similarity of identical vectors"""
        vec = np.array([1.0, 2.0, 3.0])
        
        similarity = cosine_similarity(vec, vec)
        
        self.assertAlmostEqual(similarity, 1.0)
    
    def test_cosine_similarity_orthogonal(self):
        """Test similarity of orthogonal vectors"""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        
        similarity = cosine_similarity(vec1, vec2)
        
        self.assertAlmostEqual(similarity, 0.0)
    
    def test_cosine_similarity_opposite(self):
        """Test similarity of opposite vectors"""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([-1.0, -2.0, -3.0])
        
        similarity = cosine_similarity(vec1, vec2)
        
        self.assertAlmostEqual(similarity, -1.0)
    
    def test_cosine_similarity_normalized(self):
        """Test that magnitude doesn't affect similarity"""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([2.0, 4.0, 6.0])  # Same direction, different magnitude
        
        similarity = cosine_similarity(vec1, vec2)
        
        self.assertAlmostEqual(similarity, 1.0)
    
    def test_cosine_similarity_batch(self):
        """Test batch cosine similarity calculation"""
        query = np.array([1.0, 0.0, 0.0])
        vectors = np.array([
            [1.0, 0.0, 0.0],  # Identical
            [0.0, 1.0, 0.0],  # Orthogonal
            [-1.0, 0.0, 0.0], # Opposite
            [0.7071, 0.7071, 0.0]  # 45 degrees
        ])
        
        similarities = np.array([
            cosine_similarity(query, vec) for vec in vectors
        ])
        
        self.assertAlmostEqual(similarities[0], 1.0)
        self.assertAlmostEqual(similarities[1], 0.0)
        self.assertAlmostEqual(similarities[2], -1.0)
        self.assertAlmostEqual(similarities[3], 0.7071, places=4)


class TestModuleFunctions(unittest.TestCase):
    """Test module-level convenience functions"""
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_generate_embedding_function(self, mock_ollama):
        """Test generate_embedding convenience function"""
        mock_ollama.embeddings.return_value = {
            'embedding': [0.1, 0.2, 0.3]
        }
        
        embedding = generate_embedding("Test text")
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (3,))
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_batch_generate_embeddings_function(self, mock_ollama):
        """Test batch_generate_embeddings convenience function"""
        mock_ollama.embeddings.side_effect = [
            {'embedding': [0.1, 0.2]},
            {'embedding': [0.3, 0.4]}
        ]
        
        texts = ["Text 1", "Text 2"]
        embeddings = batch_generate_embeddings(texts)
        
        self.assertEqual(len(embeddings), 2)
        for embedding in embeddings:
            self.assertIsInstance(embedding, np.ndarray)
    
    def test_singleton_client(self):
        """Test that get_embedding_client returns singleton"""
        client1 = get_embedding_client()
        client2 = get_embedding_client()
        
        self.assertIs(client1, client2)
    
    def test_singleton_reset(self):
        """Test resetting singleton client"""
        client1 = get_embedding_client()
        client2 = get_embedding_client(reset=True)
        
        self.assertIsNot(client1, client2)


class TestEmbeddingFallback(unittest.TestCase):
    """Test fallback embedding generation"""
    
    def test_hash_based_fallback(self):
        """Test hash-based fallback embeddings"""
        client = EmbeddingClient(use_fallback=True)
        
        text1 = "Test text 1"
        text2 = "Test text 2"
        text3 = "Test text 1"  # Same as text1
        
        emb1 = client._generate_fallback_embedding(text1)
        emb2 = client._generate_fallback_embedding(text2)
        emb3 = client._generate_fallback_embedding(text3)
        
        # Same text should give same embedding
        np.testing.assert_array_equal(emb1, emb3)
        
        # Different texts should give different embeddings
        self.assertFalse(np.array_equal(emb1, emb2))
        
        # Should have correct dimension
        self.assertEqual(emb1.shape, (768,))
        
        # Should be normalized
        self.assertAlmostEqual(np.linalg.norm(emb1), 1.0, places=5)
    
    def test_fallback_consistency(self):
        """Test that fallback embeddings are consistent"""
        client1 = EmbeddingClient(use_fallback=True)
        client2 = EmbeddingClient(use_fallback=True)
        
        text = "Consistent fallback test"
        
        emb1 = client1._generate_fallback_embedding(text)
        emb2 = client2._generate_fallback_embedding(text)
        
        # Should be identical across instances
        np.testing.assert_array_equal(emb1, emb2)


class TestEmbeddingIntegration(unittest.TestCase):
    """Integration tests for embedding system"""
    
    @patch('src.triz_tools.embeddings.ollama')
    def test_embedding_with_search(self, mock_ollama):
        """Test embedding integration with search functionality"""
        # Mock embeddings
        mock_ollama.embeddings.side_effect = [
            {'embedding': [0.9, 0.1, 0.0]},  # Query
            {'embedding': [0.8, 0.2, 0.0]},  # Doc 1 (similar)
            {'embedding': [0.0, 0.9, 0.1]},  # Doc 2 (different)
            {'embedding': [0.85, 0.15, 0.0]} # Doc 3 (very similar)
        ]
        
        # Generate embeddings
        query_emb = generate_embedding("Query text")
        doc_embs = batch_generate_embeddings([
            "Similar document",
            "Different document",
            "Very similar document"
        ])
        
        # Calculate similarities
        similarities = [
            cosine_similarity(query_emb, doc_emb)
            for doc_emb in doc_embs
        ]
        
        # Rank by similarity
        ranked_indices = np.argsort(similarities)[::-1]
        
        # Most similar should be doc 3, then doc 1, then doc 2
        self.assertEqual(ranked_indices[0], 2)  # Very similar
        self.assertEqual(ranked_indices[1], 0)  # Similar
        self.assertEqual(ranked_indices[2], 1)  # Different
    
    def test_embedding_dimension_consistency(self):
        """Test that all embeddings have consistent dimensions"""
        client = EmbeddingClient(embedding_dim=384)
        
        # Fallback should respect dimension
        fallback_emb = client._generate_fallback_embedding("Test")
        self.assertEqual(fallback_emb.shape, (384,))
        
        # Client should maintain dimension
        self.assertEqual(client.embedding_dim, 384)


if __name__ == '__main__':
    unittest.main()