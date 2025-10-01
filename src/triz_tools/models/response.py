"""
TRIZ Tool Response Model
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class WorkflowStage(Enum):
    """Workflow progression stages"""
    PROBLEM_DEFINITION = "problem_definition"
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    PRINCIPLE_SELECTION = "principle_selection"
    SOLUTION_GENERATION = "solution_generation"
    EVALUATION = "evaluation"
    COMPLETED = "completed"


class WorkflowType(Enum):
    """Types of TRIZ workflows"""
    GUIDED = "guided"
    AUTONOMOUS = "autonomous"
    TOOL = "tool"


@dataclass
class TRIZToolResponse:
    """Standard response format for all TRIZ tools"""
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    stage: Optional[WorkflowStage] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "session_id": self.session_id,
            "stage": self.stage.value if self.stage else None,
        }