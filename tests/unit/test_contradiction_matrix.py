#!/usr/bin/env python3
"""
Unit Tests: Contradiction Matrix (T058)
Tests for TRIZ contradiction matrix operations and lookups.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
from typing import List, Dict, Any

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.contradiction_matrix import (
    ContradictionMatrix,
    get_matrix_lookup,
    EngineeringParameter,
    MatrixEntry,
    lookup_contradiction,
    get_parameter_info,
    get_all_parameters
)


class TestEngineeringParameter(unittest.TestCase):
    """Test EngineeringParameter data structure"""
    
    def test_parameter_creation(self):
        """Test creating an engineering parameter"""
        param = EngineeringParameter(
            id=1,
            name="Weight of moving object",
            description="Mass of object in motion",
            examples=["Car weight", "Aircraft mass"],
            category="Physical"
        )
        
        self.assertEqual(param.id, 1)
        self.assertEqual(param.name, "Weight of moving object")
        self.assertEqual(param.category, "Physical")
        self.assertIn("Car weight", param.examples)
    
    def test_parameter_to_dict(self):
        """Test parameter serialization"""
        param = EngineeringParameter(
            id=14,
            name="Strength",
            description="Ability to withstand force"
        )
        
        data = param.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['id'], 14)
        self.assertEqual(data['name'], "Strength")
        self.assertIn('description', data)
    
    def test_parameter_from_dict(self):
        """Test parameter deserialization"""
        data = {
            'id': 21,
            'name': 'Power',
            'description': 'Rate of energy use',
            'examples': ['Engine power'],
            'category': 'Energy'
        }
        
        param = EngineeringParameter.from_dict(data)
        
        self.assertEqual(param.id, 21)
        self.assertEqual(param.name, 'Power')
        self.assertEqual(param.category, 'Energy')


class TestMatrixEntry(unittest.TestCase):
    """Test MatrixEntry data structure"""
    
    def test_matrix_entry_creation(self):
        """Test creating a matrix entry"""
        entry = MatrixEntry(
            improving_parameter=1,
            worsening_parameter=14,
            recommended_principles=[1, 8, 15, 40]
        )
        
        self.assertEqual(entry.improving_parameter, 1)
        self.assertEqual(entry.worsening_parameter, 14)
        self.assertEqual(len(entry.recommended_principles), 4)
        self.assertIn(15, entry.recommended_principles)
    
    def test_matrix_entry_empty(self):
        """Test matrix entry with no recommendations"""
        entry = MatrixEntry(
            improving_parameter=5,
            worsening_parameter=5,
            recommended_principles=[]
        )
        
        self.assertEqual(len(entry.recommended_principles), 0)
    
    def test_matrix_entry_to_dict(self):
        """Test matrix entry serialization"""
        entry = MatrixEntry(
            improving_parameter=2,
            worsening_parameter=11,
            recommended_principles=[2, 14, 30]
        )
        
        data = entry.to_dict()
        
        self.assertEqual(data['improving'], 2)
        self.assertEqual(data['worsening'], 11)
        self.assertEqual(data['principles'], [2, 14, 30])


class TestContradictionMatrix(unittest.TestCase):
    """Test ContradictionMatrix operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.matrix = ContradictionMatrix()
        
        # Add test parameters
        self.matrix.add_parameter(
            1, "Weight of moving object",
            "Mass of object in motion"
        )
        self.matrix.add_parameter(
            14, "Strength",
            "Ability to withstand force"
        )
        self.matrix.add_parameter(
            21, "Power",
            "Rate of energy use"
        )
        
        # Add test matrix entries
        self.matrix.add_entry(1, 14, [1, 8, 15, 40])
        self.matrix.add_entry(1, 21, [2, 14, 35])
        self.matrix.add_entry(14, 1, [40, 26, 27, 1])
    
    def test_add_parameter(self):
        """Test adding parameters to matrix"""
        success = self.matrix.add_parameter(
            39, "Productivity",
            "Output per unit time"
        )
        
        self.assertTrue(success)
        self.assertIn(39, self.matrix.parameters)
        
        param = self.matrix.parameters[39]
        self.assertEqual(param.name, "Productivity")
    
    def test_add_entry(self):
        """Test adding matrix entries"""
        success = self.matrix.add_entry(21, 14, [19, 35, 38])
        
        self.assertTrue(success)
        
        # Verify entry exists
        key = (21, 14)
        self.assertIn(key, self.matrix.matrix)
        self.assertEqual(self.matrix.matrix[key], [19, 35, 38])
    
    def test_lookup_contradiction(self):
        """Test looking up contradictions"""
        result = self.matrix.lookup(1, 14)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MatrixEntry)
        self.assertEqual(result.improving_parameter, 1)
        self.assertEqual(result.worsening_parameter, 14)
        self.assertEqual(result.recommended_principles, [1, 8, 15, 40])
    
    def test_lookup_reverse(self):
        """Test that reverse lookup gives different results"""
        forward = self.matrix.lookup(1, 14)
        reverse = self.matrix.lookup(14, 1)
        
        self.assertIsNotNone(forward)
        self.assertIsNotNone(reverse)
        self.assertNotEqual(
            forward.recommended_principles,
            reverse.recommended_principles
        )
    
    def test_lookup_nonexistent(self):
        """Test looking up non-existent contradiction"""
        result = self.matrix.lookup(99, 88)
        
        self.assertIsNone(result)
    
    def test_lookup_same_parameter(self):
        """Test looking up same parameter (no contradiction)"""
        result = self.matrix.lookup(1, 1)
        
        self.assertIsNone(result)
    
    def test_get_parameter(self):
        """Test getting parameter by ID"""
        param = self.matrix.get_parameter(14)
        
        self.assertIsNotNone(param)
        self.assertEqual(param.name, "Strength")
        
        # Non-existent parameter
        param = self.matrix.get_parameter(999)
        self.assertIsNone(param)
    
    def test_get_all_parameters(self):
        """Test getting all parameters"""
        params = self.matrix.get_all_parameters()
        
        self.assertEqual(len(params), 3)
        self.assertIsInstance(params[0], EngineeringParameter)
        
        # Should be sorted by ID
        ids = [p.id for p in params]
        self.assertEqual(ids, sorted(ids))
    
    def test_find_parameters_by_keyword(self):
        """Test finding parameters by keyword"""
        results = self.matrix.find_parameters_by_keyword("weight")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, 1)
        
        # Case insensitive
        results = self.matrix.find_parameters_by_keyword("STRENGTH")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, 14)
    
    def test_get_principles_for_parameter(self):
        """Test getting all principles for a parameter"""
        principles = self.matrix.get_principles_for_parameter(1)
        
        # Should include principles from all entries where 1 is improving
        self.assertIn(1, principles)   # From (1, 14)
        self.assertIn(8, principles)   # From (1, 14)
        self.assertIn(2, principles)   # From (1, 21)
        self.assertIn(35, principles)  # From (1, 21)
    
    def test_save_and_load(self):
        """Test matrix persistence"""
        temp_file = Path(tempfile.mktemp(suffix=".json"))
        
        try:
            # Save matrix
            self.matrix.save(temp_file)
            self.assertTrue(temp_file.exists())
            
            # Load into new matrix
            new_matrix = ContradictionMatrix()
            new_matrix.load(temp_file)
            
            # Verify data
            self.assertEqual(len(new_matrix.parameters), 3)
            self.assertEqual(len(new_matrix.matrix), 3)
            
            # Check specific entry
            result = new_matrix.lookup(1, 14)
            self.assertIsNotNone(result)
            self.assertEqual(result.recommended_principles, [1, 8, 15, 40])
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    def test_export_to_csv(self):
        """Test exporting matrix to CSV"""
        temp_file = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            self.matrix.export_to_csv(temp_file)
            self.assertTrue(temp_file.exists())
            
            # Read and verify CSV
            import csv
            with open(temp_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Should have header + data rows
            self.assertGreater(len(rows), 1)
            
            # Check header
            self.assertIn("Improving", rows[0])
            self.assertIn("Worsening", rows[0])
            self.assertIn("Principles", rows[0])
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    def test_import_from_csv(self):
        """Test importing matrix from CSV"""
        temp_file = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            # Create test CSV
            import csv
            with open(temp_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Improving", "Worsening", "Principles"])
                writer.writerow(["5", "10", "1,2,3"])
                writer.writerow(["10", "5", "4,5,6"])
            
            # Import
            new_matrix = ContradictionMatrix()
            count = new_matrix.import_from_csv(temp_file)
            
            self.assertEqual(count, 2)
            
            # Verify entries
            result = new_matrix.lookup(5, 10)
            self.assertIsNotNone(result)
            self.assertEqual(result.recommended_principles, [1, 2, 3])
        finally:
            if temp_file.exists():
                temp_file.unlink()


class TestContradictionMatrixStandard(unittest.TestCase):
    """Test standard TRIZ contradiction matrix"""
    
    def setUp(self):
        """Set up with standard matrix"""
        self.matrix = ContradictionMatrix()
        self.matrix.load_standard_matrix()
    
    def test_standard_matrix_loaded(self):
        """Test that standard matrix has correct size"""
        params = self.matrix.get_all_parameters()
        
        # Should have 39 parameters
        self.assertEqual(len(params), 39)
        
        # Check some known parameters
        weight = self.matrix.get_parameter(1)
        self.assertIsNotNone(weight)
        self.assertIn("Weight", weight.name)
        
        productivity = self.matrix.get_parameter(39)
        self.assertIsNotNone(productivity)
        self.assertIn("Productivity", productivity.name)
    
    def test_known_contradiction(self):
        """Test a known contradiction from standard matrix"""
        # Weight vs Strength is a classic contradiction
        result = self.matrix.lookup(1, 14)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result.recommended_principles, list)
        self.assertTrue(len(result.recommended_principles) > 0)
        
        # Common principles for this contradiction
        # Often includes segmentation (1), composite materials (40)
        principles = result.recommended_principles
        self.assertTrue(1 in principles or 40 in principles)
    
    def test_matrix_completeness(self):
        """Test that matrix has entries for most combinations"""
        total_combinations = 0
        filled_combinations = 0
        
        for i in range(1, 40):
            for j in range(1, 40):
                if i != j:
                    total_combinations += 1
                    if self.matrix.lookup(i, j) is not None:
                        filled_combinations += 1
        
        # Standard matrix is not 100% complete but should have many entries
        fill_rate = filled_combinations / total_combinations
        self.assertGreater(fill_rate, 0.3)  # At least 30% filled
    
    def test_parameter_categories(self):
        """Test that parameters have categories"""
        params = self.matrix.get_all_parameters()
        
        categories = set()
        for param in params:
            if param.category:
                categories.add(param.category)
        
        # Should have multiple categories
        self.assertGreater(len(categories), 0)


class TestMatrixSingleton(unittest.TestCase):
    """Test singleton pattern for matrix"""
    
    def test_singleton_instance(self):
        """Test that get_matrix_lookup returns singleton"""
        matrix1 = get_matrix_lookup()
        matrix2 = get_matrix_lookup()
        
        self.assertIs(matrix1, matrix2)
    
    def test_singleton_reset(self):
        """Test resetting singleton instance"""
        matrix1 = get_matrix_lookup()
        matrix1.add_parameter(99, "Test", "Test param")
        
        matrix2 = get_matrix_lookup(reset=True)
        
        self.assertIsNot(matrix1, matrix2)
        
        # New instance shouldn't have test parameter
        self.assertIsNone(matrix2.get_parameter(99))


class TestModuleFunctions(unittest.TestCase):
    """Test module-level convenience functions"""
    
    def setUp(self):
        """Set up test environment"""
        # Reset and initialize matrix
        matrix = get_matrix_lookup(reset=True)
        matrix.load_standard_matrix()
    
    def test_lookup_contradiction_function(self):
        """Test lookup_contradiction convenience function"""
        result = lookup_contradiction(1, 14)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn('improving', result)
        self.assertIn('worsening', result)
        self.assertIn('principles', result)
    
    def test_get_parameter_info_function(self):
        """Test get_parameter_info convenience function"""
        info = get_parameter_info(1)
        
        self.assertIsNotNone(info)
        self.assertIsInstance(info, dict)
        self.assertIn('id', info)
        self.assertIn('name', info)
        self.assertEqual(info['id'], 1)
    
    def test_get_all_parameters_function(self):
        """Test get_all_parameters convenience function"""
        params = get_all_parameters()
        
        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 39)
        
        # Each should be a dict
        for param in params:
            self.assertIsInstance(param, dict)
            self.assertIn('id', param)
            self.assertIn('name', param)


class TestMatrixAnalysis(unittest.TestCase):
    """Test matrix analysis functions"""
    
    def setUp(self):
        """Set up with standard matrix"""
        self.matrix = ContradictionMatrix()
        self.matrix.load_standard_matrix()
    
    def test_most_common_principles(self):
        """Test finding most commonly recommended principles"""
        principle_counts = {}
        
        # Count principle occurrences
        for i in range(1, 40):
            for j in range(1, 40):
                if i != j:
                    result = self.matrix.lookup(i, j)
                    if result:
                        for principle in result.recommended_principles:
                            principle_counts[principle] = \
                                principle_counts.get(principle, 0) + 1
        
        # Find most common
        if principle_counts:
            most_common = max(principle_counts, key=principle_counts.get)
            
            # Principle 35 (Parameter changes) is often very common
            # Principle 1 (Segmentation) is also common
            self.assertIn(most_common, [1, 2, 35, 10, 13])
    
    def test_parameter_conflict_frequency(self):
        """Test which parameters most often conflict"""
        conflict_counts = {}
        
        for i in range(1, 40):
            conflicts = 0
            for j in range(1, 40):
                if i != j and self.matrix.lookup(i, j) is not None:
                    conflicts += 1
            conflict_counts[i] = conflicts
        
        # All parameters should have some conflicts
        for param_id, count in conflict_counts.items():
            self.assertGreater(count, 0, 
                             f"Parameter {param_id} has no conflicts")
    
    def test_principle_applicability(self):
        """Test which principles apply to which parameter pairs"""
        # Test if certain principles are recommended for weight problems
        weight_principles = set()
        
        for j in range(1, 40):
            if j != 1:
                result = self.matrix.lookup(1, j)  # Weight improving
                if result:
                    weight_principles.update(result.recommended_principles)
        
        # Weight problems often involve these principles
        common_weight_principles = [1, 2, 8, 14, 26, 35, 40]
        
        # At least some should be present
        found = sum(1 for p in common_weight_principles if p in weight_principles)
        self.assertGreater(found, 2)


if __name__ == '__main__':
    unittest.main()