"""
Response Models for TRIZ Tools
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class WorkflowType(Enum):
    """Type of TRIZ workflow"""
    GUIDED = "guided"
    AUTONOMOUS = "autonomous"
    TOOL = "tool"


class WorkflowStage(Enum):
    """Stages in TRIZ workflow"""
    PROBLEM_DEFINITION = "problem_definition"
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    PRINCIPLE_SELECTION = "principle_selection"
    SOLUTION_GENERATION = "solution_generation"
    EVALUATION = "evaluation"
    COMPLETED = "completed"


@dataclass
class TRIZToolResponse:
    """Standard response format for all TRIZ tools"""
    success: bool
    message: str
    data: Dict[str, Any]
    session_id: Optional[str] = None
    stage: Optional[WorkflowStage] = None
