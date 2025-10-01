"""
TRIZ Tool Models
Core data models for TRIZ Co-Pilot
"""

from .response import TRIZToolResponse, WorkflowStage, WorkflowType
from .contradiction import ContradictionResult, ContradictionMatrix
from .principle import TRIZPrinciple, TRIZKnowledgeBase
from .solution import SolutionConcept, AnalysisReport
from .session import ProblemSession

__all__ = [
    # Response models
    "TRIZToolResponse",
    "WorkflowStage",
    "WorkflowType",

    # Contradiction models
    "ContradictionResult",
    "ContradictionMatrix",

    # Principle models
    "TRIZPrinciple",
    "TRIZKnowledgeBase",

    # Solution models
    "SolutionConcept",
    "AnalysisReport",

    # Session models
    "ProblemSession",
]
