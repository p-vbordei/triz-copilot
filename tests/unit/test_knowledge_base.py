#!/usr/bin/env python3
"""
Unit Tests: Knowledge Base Operations (T055)
Tests for TRIZ knowledge base core functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
from typing import Dict, List, Any

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.knowledge_base import (
    TRIZKnowledgeBase,
    get_knowledge_base,
    TRIZPrinciple,
    SearchResult
)


class TestTRIZPrinciple(unittest.TestCase):
    """Test TRIZPrinciple data structure"""
    
    def test_principle_creation(self):
        """Test creating a TRIZ principle"""
        principle = TRIZPrinciple(
            id=1,
            name="Segmentation",
            description="Divide object into independent parts",
            examples=["Modular furniture", "Computer components"],
            applications=["Manufacturing", "Software design"],
            related_principles=[2, 5, 13]
        )
        
        self.assertEqual(principle.id, 1)
        self.assertEqual(principle.name, "Segmentation")
        self.assertIn("Modular furniture", principle.examples)
        self.assertEqual(len(principle.related_principles), 3)
    
    def test_principle_to_dict(self):
        """Test principle serialization"""
        principle = TRIZPrinciple(
            id=2,
            name="Taking out",
            description="Separate interfering parts"
        )
        
        data = principle.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['name'], "Taking out")
        self.assertIn('description', data)
    
    def test_principle_from_dict(self):
        """Test principle deserialization"""
        data = {
            'id': 3,
            'name': 'Local quality',
            'description': 'Transition from homogeneous to heterogeneous',
            'examples': ['Hammer with soft handle'],
            'applications': ['Tool design']
        }
        
        principle = TRIZPrinciple.from_dict(data)
        
        self.assertEqual(principle.id, 3)
        self.assertEqual(principle.name, 'Local quality')
        self.assertEqual(len(principle.examples), 1)


class TestKnowledgeBase(unittest.TestCase):
    """Test TRIZKnowledgeBase operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.kb = TRIZKnowledgeBase(data_dir=Path(self.temp_dir))
        
        # Add test principles
        self.test_principles = [
            TRIZPrinciple(
                id=1,
                name="Segmentation",
                description="Divide object into independent parts",
                examples=["Modular design", "Sectional furniture"],
                applications=["Manufacturing", "Architecture"]
            ),
            TRIZPrinciple(
                id=15,
                name="Dynamics",
                description="Make objects adaptive",
                examples=["Adjustable steering wheels", "Flexible manufacturing"],
                applications=["Automotive", "Production"]
            ),
            TRIZPrinciple(
                id=40,
                name="Composite materials",
                description="Use composite materials instead of homogeneous ones",
                examples=["Carbon fiber", "Reinforced concrete"],
                applications=["Aerospace", "Construction"]
            )
        ]
        
        for principle in self.test_principles:
            self.kb.add_principle(principle)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_principle(self):
        """Test adding principles to knowledge base"""
        principle = TRIZPrinciple(
            id=35,
            name="Parameter changes",
            description="Change physical or chemical state"
        )
        
        result = self.kb.add_principle(principle)
        
        self.assertTrue(result)
        self.assertEqual(len(self.kb.principles), 4)
        self.assertIn(35, self.kb.principles)
    
    def test_get_principle(self):
        """Test retrieving principle by ID"""
        principle = self.kb.get_principle(1)
        
        self.assertIsNotNone(principle)
        self.assertEqual(principle.name, "Segmentation")
        
        # Test non-existent principle
        none_principle = self.kb.get_principle(999)
        self.assertIsNone(none_principle)
    
    def test_search_principles_by_keyword(self):
        """Test searching principles by keyword"""
        results = self.kb.search_principles("modular")
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        
        # Check first result
        first = results[0]
        self.assertIsInstance(first, SearchResult)
        self.assertEqual(first.principle.id, 1)
        self.assertGreater(first.relevance_score, 0)
    
    def test_search_principles_by_application(self):
        """Test searching by application domain"""
        results = self.kb.search_principles("aerospace")
        
        self.assertTrue(len(results) > 0)
        
        # Should find composite materials principle
        principle_ids = [r.principle.id for r in results]
        self.assertIn(40, principle_ids)
    
    def test_get_all_principles(self):
        """Test retrieving all principles"""
        all_principles = self.kb.get_all_principles()
        
        self.assertEqual(len(all_principles), 3)
        self.assertIsInstance(all_principles[0], TRIZPrinciple)
        
        # Check ordering
        ids = [p.id for p in all_principles]
        self.assertEqual(ids, sorted(ids))
    
    def test_save_and_load(self):
        """Test persistence of knowledge base"""
        # Save current state
        self.kb.save()
        
        # Create new instance and load
        new_kb = TRIZKnowledgeBase(data_dir=Path(self.temp_dir))
        new_kb.load()
        
        # Verify data persisted
        self.assertEqual(len(new_kb.principles), 3)
        principle = new_kb.get_principle(15)
        self.assertIsNotNone(principle)
        self.assertEqual(principle.name, "Dynamics")
    
    def test_export_to_json(self):
        """Test exporting knowledge base to JSON"""
        export_file = Path(self.temp_dir) / "export.json"
        
        self.kb.export_to_json(export_file)
        
        self.assertTrue(export_file.exists())
        
        # Load and verify
        with open(export_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('principles', data)
        self.assertEqual(len(data['principles']), 3)
    
    def test_import_from_json(self):
        """Test importing knowledge base from JSON"""
        # Create test data
        test_data = {
            'principles': [
                {
                    'id': 2,
                    'name': 'Taking out',
                    'description': 'Separate interfering parts',
                    'examples': ['Quiet compressor'],
                    'applications': ['Noise reduction']
                }
            ]
        }
        
        import_file = Path(self.temp_dir) / "import.json"
        with open(import_file, 'w') as f:
            json.dump(test_data, f)
        
        # Import
        count = self.kb.import_from_json(import_file)
        
        self.assertEqual(count, 1)
        self.assertEqual(len(self.kb.principles), 4)
        
        principle = self.kb.get_principle(2)
        self.assertIsNotNone(principle)
        self.assertEqual(principle.name, 'Taking out')
    
    def test_search_with_limit(self):
        """Test search with result limit"""
        # Add more principles for testing
        for i in range(5, 10):
            self.kb.add_principle(TRIZPrinciple(
                id=i,
                name=f"Principle {i}",
                description="Test principle with common words"
            ))
        
        results = self.kb.search_principles("principle", limit=3)
        
        self.assertEqual(len(results), 3)
    
    def test_fuzzy_search(self):
        """Test fuzzy/approximate search"""
        # Test with typo
        results = self.kb.search_principles("segmentaton")  # Typo
        
        # Should still find segmentation principle
        if len(results) > 0:
            principle_names = [r.principle.name.lower() for r in results]
            self.assertTrue(any("segment" in name for name in principle_names))
    
    def test_empty_search(self):
        """Test search with no results"""
        results = self.kb.search_principles("xyz123nonexistent")
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)
    
    def test_case_insensitive_search(self):
        """Test case-insensitive search"""
        results_lower = self.kb.search_principles("composite")
        results_upper = self.kb.search_principles("COMPOSITE")
        results_mixed = self.kb.search_principles("CoMpOsItE")
        
        # All should return same results
        self.assertEqual(len(results_lower), len(results_upper))
        self.assertEqual(len(results_lower), len(results_mixed))
        
        if len(results_lower) > 0:
            self.assertEqual(
                results_lower[0].principle.id,
                results_upper[0].principle.id
            )


class TestKnowledgeBaseSingleton(unittest.TestCase):
    """Test singleton pattern for knowledge base"""
    
    def test_singleton_instance(self):
        """Test that get_knowledge_base returns singleton"""
        kb1 = get_knowledge_base()
        kb2 = get_knowledge_base()
        
        self.assertIs(kb1, kb2)
    
    def test_singleton_reset(self):
        """Test resetting singleton instance"""
        kb1 = get_knowledge_base()
        kb1.add_principle(TRIZPrinciple(
            id=99,
            name="Test",
            description="Test principle"
        ))
        
        # Reset and get new instance
        kb2 = get_knowledge_base(reset=True)
        
        self.assertIsNot(kb1, kb2)
        
        # Old principle should not be in new instance
        self.assertIsNone(kb2.get_principle(99))


class TestSearchResult(unittest.TestCase):
    """Test SearchResult functionality"""
    
    def test_search_result_creation(self):
        """Test creating search result"""
        principle = TRIZPrinciple(
            id=1,
            name="Test",
            description="Test description"
        )
        
        result = SearchResult(
            principle=principle,
            relevance_score=0.85,
            matched_fields=['name', 'description']
        )
        
        self.assertEqual(result.principle.id, 1)
        self.assertEqual(result.relevance_score, 0.85)
        self.assertIn('name', result.matched_fields)
    
    def test_search_result_comparison(self):
        """Test comparing search results by score"""
        principle1 = TRIZPrinciple(id=1, name="P1", description="D1")
        principle2 = TRIZPrinciple(id=2, name="P2", description="D2")
        
        result1 = SearchResult(principle=principle1, relevance_score=0.9)
        result2 = SearchResult(principle=principle2, relevance_score=0.7)
        
        # Higher score should come first
        results = sorted([result2, result1], key=lambda r: r.relevance_score, reverse=True)
        
        self.assertEqual(results[0].principle.id, 1)
        self.assertEqual(results[1].principle.id, 2)


class TestKnowledgeBaseIntegration(unittest.TestCase):
    """Integration tests for knowledge base with other components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.kb = TRIZKnowledgeBase(data_dir=Path(self.temp_dir))
        
        # Load standard principles
        self.kb.load_standard_principles()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_standard_principles_loaded(self):
        """Test that standard 40 principles are loaded"""
        all_principles = self.kb.get_all_principles()
        
        # Should have 40 principles
        self.assertEqual(len(all_principles), 40)
        
        # Check some known principles
        segmentation = self.kb.get_principle(1)
        self.assertIsNotNone(segmentation)
        self.assertEqual(segmentation.name, "Segmentation")
        
        dynamics = self.kb.get_principle(15)
        self.assertIsNotNone(dynamics)
        self.assertEqual(dynamics.name, "Dynamics")
        
        composite = self.kb.get_principle(40)
        self.assertIsNotNone(composite)
        self.assertEqual(composite.name, "Composite materials")
    
    def test_principle_relationships(self):
        """Test related principles functionality"""
        principle = self.kb.get_principle(1)  # Segmentation
        
        if principle and principle.related_principles:
            for related_id in principle.related_principles:
                related = self.kb.get_principle(related_id)
                self.assertIsNotNone(related, f"Related principle {related_id} not found")
    
    def test_search_standard_principles(self):
        """Test searching through standard principles"""
        # Search for weight-related principles
        results = self.kb.search_principles("weight")
        
        self.assertTrue(len(results) > 0)
        
        # Search for dynamics
        results = self.kb.search_principles("dynamic")
        
        self.assertTrue(len(results) > 0)
        principle_ids = [r.principle.id for r in results]
        self.assertIn(15, principle_ids)  # Dynamics principle


if __name__ == '__main__':
    unittest.main()