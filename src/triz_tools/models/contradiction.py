"""Contradiction Models"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ContradictionResult:
    """Result of contradiction analysis"""
    improving_parameter: int
    worsening_parameter: int
    recommended_principles: List[int]
    confidence_score: float
    explanation: str
    application_frequency: int = 0

class ContradictionMatrix:
    """TRIZ Contradiction Matrix"""
    def __init__(self):
        self.matrix = {}
        self.parameters = {}

    def add_contradiction(self, improving, worsening, principles, confidence=0.7, applications=0):
        key = f"{improving}_{worsening}"
        self.matrix[key] = {
            "improving": improving,
            "worsening": worsening,
            "principles": principles,
            "confidence": confidence,
            "applications": applications
        }

    def lookup(self, improving, worsening):
        key = f"{improving}_{worsening}"
        if key in self.matrix:
            entry = self.matrix[key]
            return ContradictionResult(
                improving_parameter=entry["improving"],
                worsening_parameter=entry["worsening"],
                recommended_principles=entry["principles"],
                confidence_score=entry["confidence"],
                explanation=f"Matrix recommendation for {improving} vs {worsening}",
                application_frequency=entry.get("applications", 0)
            )
        return None

    def validate_parameters(self, imp, wor):
        if not (1 <= imp <= 39):
            return False, f"Improving parameter must be 1-39, got {imp}"
        if not (1 <= wor <= 39):
            return False, f"Worsening parameter must be 1-39, got {wor}"
        return True, "Valid"

    def get_parameter(self, param_id):
        class Param:
            def __init__(self, id):
                self.parameter_name = f"Parameter {id}"
        return Param(param_id)
