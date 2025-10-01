"""
TRIZ Co-Pilot Data Models
"""

from .knowledge_base import TRIZKnowledgeBase, TRIZPrinciple
from .contradiction_matrix import ContradictionMatrix, ContradictionResult
from .session import ProblemSession, WorkflowStage, WorkflowType
from .solution import SolutionConcept
from .materials import MaterialsDatabase, Material
from .report import AnalysisReport
from .response import TRIZToolResponse

__all__ = [
    "TRIZKnowledgeBase",
    "TRIZPrinciple",
    "ContradictionMatrix",
    "ContradictionResult",
    "ProblemSession",
    "WorkflowStage",
    "WorkflowType",
    "SolutionConcept",
    "MaterialsDatabase",
    "Material",
    "AnalysisReport",
    "TRIZToolResponse",
]