"""
Contradiction Matrix Lookup Logic (T034)
Provides efficient lookup and analysis of TRIZ contradiction matrix.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

from .models.contradiction import (
    ContradictionMatrix,
    ContradictionResult,
)
from .models import TRIZPrinciple

# EngineeringParameter and MatrixEntry don't exist, define them here if needed
class EngineeringParameter:
    """Engineering parameter for contradiction matrix"""
    def __init__(self, id: int, name: str, description: str = ""):
        self.id = id
        self.name = name
        self.description = description


class MatrixEntry:
    """Matrix entry for contradiction resolution"""
    def __init__(self, improving: int, worsening: int, principles: List[int]):
        self.improving = improving
        self.worsening = worsening
        self.principles = principles
        self.improving_parameter = improving
        self.worsening_parameter = worsening

logger = logging.getLogger(__name__)


class ContradictionMatrixLookup:
    """Enhanced contradiction matrix lookup with analysis"""
    
    def __init__(self, matrix_file: Optional[Path] = None):
        """
        Initialize matrix lookup.
        
        Args:
            matrix_file: Path to matrix JSON file
        """
        self.matrix = ContradictionMatrix()
        self._load_matrix_data(matrix_file)
        self._build_reverse_index()
        
        logger.info("Contradiction matrix lookup initialized")
    
    def _load_matrix_data(self, matrix_file: Optional[Path] = None):
        """Load matrix data from file"""
        if matrix_file is None:
            matrix_file = Path(__file__).parent / "data" / "contradiction_matrix.json"
        
        if not matrix_file.exists():
            logger.warning(f"Matrix file not found: {matrix_file}")
            self._load_default_matrix()
            return
        
        try:
            with open(matrix_file, "r") as f:
                data = json.load(f)
            
            # Load matrix entries
            for entry_key, entry_data in data.get("matrix", {}).items():
                self.matrix.add_contradiction(
                    improving=entry_data["improving"],
                    worsening=entry_data["worsening"],
                    principles=entry_data["principles"],
                    confidence=entry_data.get("confidence", 0.7),
                    applications=entry_data.get("applications", 0)
                )
            
            logger.info(f"Loaded {len(self.matrix.matrix)} matrix entries")
            
        except Exception as e:
            logger.error(f"Failed to load matrix: {str(e)}")
            self._load_default_matrix()
    
    def _load_default_matrix(self):
        """Load default matrix entries"""
        # Common contradictions with recommended principles
        default_entries = [
            # Weight vs Strength
            (1, 14, [1, 8, 15, 40], 0.9, 100),
            (1, 11, [1, 8, 15, 40], 0.9, 95),
            
            # Speed vs Accuracy
            (6, 28, [2, 14, 29, 30], 0.8, 80),
            
            # Productivity vs Quality
            (29, 28, [10, 18, 32, 39], 0.85, 90),
            
            # Temperature vs Material damage
            (16, 13, [19, 35, 36, 37], 0.8, 70),
            
            # Force vs Energy consumption
            (7, 18, [2, 14, 35, 40], 0.75, 60),
            
            # Complexity vs Usability
            (36, 33, [1, 2, 13, 27], 0.8, 85),
            
            # Automation vs Flexibility
            (38, 35, [1, 15, 24, 35], 0.7, 50),
        ]
        
        for improving, worsening, principles, confidence, applications in default_entries:
            self.matrix.add_contradiction(
                improving, worsening, principles, confidence, applications
            )
    
    def _build_reverse_index(self):
        """Build reverse index for principle lookup"""
        self.principle_to_contradictions = {}

        for key, result in self.matrix.matrix.items():
            # Handle both dict and ContradictionResult
            principles = result.get("principles", []) if isinstance(result, dict) else result.recommended_principles
            for principle in principles:
                if principle not in self.principle_to_contradictions:
                    self.principle_to_contradictions[principle] = []
                self.principle_to_contradictions[principle].append(key)
    
    def lookup(
        self,
        improving: int,
        worsening: int
    ) -> Optional[ContradictionResult]:
        """
        Look up a specific contradiction.
        
        Args:
            improving: Improving parameter (1-39)
            worsening: Worsening parameter (1-39)
        
        Returns:
            Contradiction result or None
        """
        # Validate parameters
        valid, message = self.matrix.validate_parameters(improving, worsening)
        if not valid:
            logger.warning(f"Invalid parameters: {message}")
            return None
        
        return self.matrix.lookup(improving, worsening)
    
    def find_similar_contradictions(
        self,
        improving: int,
        worsening: int,
        max_results: int = 5
    ) -> List[Tuple[Tuple[int, int], ContradictionResult]]:
        """
        Find similar contradictions.
        
        Args:
            improving: Improving parameter
            worsening: Worsening parameter
            max_results: Maximum results to return
        
        Returns:
            List of similar contradictions
        """
        results = []
        
        # Look for contradictions with same improving parameter
        for key, result in self.matrix.matrix.items():
            if key[0] == improving and key[1] != worsening:
                results.append((key, result))
        
        # Look for contradictions with same worsening parameter
        for key, result in self.matrix.matrix.items():
            if key[1] == worsening and key[0] != improving:
                results.append((key, result))
        
        # Sort by confidence and applications
        results.sort(
            key=lambda x: (x[1].confidence_score, x[1].application_frequency),
            reverse=True
        )
        
        return results[:max_results]
    
    def find_contradictions_for_principle(
        self,
        principle_id: int
    ) -> List[Tuple[Tuple[int, int], ContradictionResult]]:
        """
        Find all contradictions that recommend a specific principle.
        
        Args:
            principle_id: TRIZ principle number (1-40)
        
        Returns:
            List of contradictions recommending this principle
        """
        results = []
        
        contradiction_keys = self.principle_to_contradictions.get(principle_id, [])
        
        for key in contradiction_keys:
            result = self.matrix.matrix.get(key)
            if result:
                results.append((key, result))
        
        return results
    
    def get_most_used_principles(self, top_k: int = 10) -> List[Tuple[int, int]]:
        """
        Get most frequently recommended principles.
        
        Args:
            top_k: Number of top principles
        
        Returns:
            List of (principle_id, usage_count) tuples
        """
        principle_counts = {}
        
        for result in self.matrix.matrix.values():
            for principle in result.recommended_principles:
                principle_counts[principle] = principle_counts.get(principle, 0) + 1
        
        sorted_principles = sorted(
            principle_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_principles[:top_k]
    
    def analyze_parameter_relationships(
        self,
        parameter_id: int
    ) -> Dict[str, Any]:
        """
        Analyze relationships for a specific parameter.
        
        Args:
            parameter_id: Parameter ID (1-39)
        
        Returns:
            Analysis of parameter relationships
        """
        improves_with = []
        worsens_with = []
        principles_when_improving = {}
        principles_when_worsening = {}
        
        for key, result in self.matrix.matrix.items():
            if key[0] == parameter_id:
                # This parameter is improving
                worsens_with.append(key[1])
                for principle in result.recommended_principles:
                    principles_when_improving[principle] = \
                        principles_when_improving.get(principle, 0) + 1
            
            if key[1] == parameter_id:
                # This parameter is worsening
                improves_with.append(key[0])
                for principle in result.recommended_principles:
                    principles_when_worsening[principle] = \
                        principles_when_worsening.get(principle, 0) + 1
        
        # Get parameter info
        parameter = self.matrix.get_parameter(parameter_id)
        
        return {
            "parameter_id": parameter_id,
            "parameter_name": parameter.parameter_name if parameter else f"Parameter {parameter_id}",
            "frequently_improves_with": list(set(improves_with)),
            "frequently_worsens_with": list(set(worsens_with)),
            "principles_when_improving": dict(sorted(
                principles_when_improving.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "principles_when_worsening": dict(sorted(
                principles_when_worsening.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }
    
    def suggest_alternative_formulations(
        self,
        improving: int,
        worsening: int
    ) -> List[Dict[str, Any]]:
        """
        Suggest alternative problem formulations.
        
        Args:
            improving: Current improving parameter
            worsening: Current worsening parameter
        
        Returns:
            List of alternative formulations
        """
        alternatives = []
        
        # Look for related parameters
        related_improving = self._find_related_parameters(improving)
        related_worsening = self._find_related_parameters(worsening)
        
        for alt_imp in related_improving[:3]:
            result = self.matrix.lookup(alt_imp, worsening)
            if result:
                alternatives.append({
                    "improving": alt_imp,
                    "worsening": worsening,
                    "description": f"Consider improving {self.matrix.get_parameter(alt_imp).parameter_name} instead",
                    "principles": result.recommended_principles[:3],
                    "confidence": result.confidence_score
                })
        
        for alt_wor in related_worsening[:3]:
            result = self.matrix.lookup(improving, alt_wor)
            if result:
                alternatives.append({
                    "improving": improving,
                    "worsening": alt_wor,
                    "description": f"Accept worsening {self.matrix.get_parameter(alt_wor).parameter_name} instead",
                    "principles": result.recommended_principles[:3],
                    "confidence": result.confidence_score
                })
        
        return alternatives
    
    def _find_related_parameters(self, parameter_id: int) -> List[int]:
        """Find parameters related to given parameter"""
        # Group related parameters by category
        parameter_groups = [
            [1, 2],  # Weight
            [3, 4, 5],  # Dimensions
            [6, 9, 19, 20],  # Motion
            [7, 8, 10, 11],  # Force/Strength
            [14, 15, 27],  # Reliability
            [16, 17],  # Temperature/Light
            [18, 21, 22],  # Energy
            [28, 29, 39],  # Productivity/Accuracy
            [32, 33, 34, 35],  # Manufacturability/Usability
            [36, 37, 38],  # Complexity/Control
        ]
        
        for group in parameter_groups:
            if parameter_id in group:
                return [p for p in group if p != parameter_id]
        
        return []


# Singleton instance
_matrix_lookup: Optional[ContradictionMatrixLookup] = None


def get_matrix_lookup(
    matrix_file: Optional[Path] = None,
    reset: bool = False
) -> ContradictionMatrixLookup:
    """Get or create matrix lookup singleton"""
    global _matrix_lookup

    if reset or _matrix_lookup is None:
        _matrix_lookup = ContradictionMatrixLookup(matrix_file=matrix_file)

    return _matrix_lookup


def lookup_contradiction(improving: int, worsening: int) -> List[int]:
    """Lookup contradiction in matrix (convenience function)"""
    lookup = get_matrix_lookup()
    result = lookup.lookup(improving, worsening)
    return result.get("principles", []) if result else []


def get_parameter_info(parameter_id: int) -> Optional[Dict[str, Any]]:
    """Get information about a parameter"""
    lookup = get_matrix_lookup()
    if hasattr(lookup, 'parameters') and parameter_id in lookup.parameters:
        return lookup.parameters[parameter_id]
    return None


def get_all_parameters() -> List[Dict[str, Any]]:
    """Get all engineering parameters"""
    lookup = get_matrix_lookup()
    if hasattr(lookup, 'parameters'):
        return [{"id": k, **v} for k, v in lookup.parameters.items()]
    return []