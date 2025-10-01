"""Solution and Analysis Models"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class SolutionConcept:
    """Generated solution concept"""
    concept_title: str
    description: str
    applied_principles: List[int]
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    feasibility_score: float = 0.7
    innovation_level: int = 3

@dataclass
class AnalysisReport:
    """Complete TRIZ analysis report"""
    problem_statement: str
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    recommended_principles: List[int] = field(default_factory=list)
    solution_concepts: List[SolutionConcept] = field(default_factory=list)
    implementation_plan: Dict[str, Any] = field(default_factory=dict)
    estimated_impact: Dict[str, float] = field(default_factory=dict)
