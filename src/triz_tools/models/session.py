"""Session Models"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class ProblemSession:
    """TRIZ problem-solving session"""
    session_id: str
    problem_statement: str
    stage: str = "problem_definition"
    user_inputs: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    platform: str = "gemini"  # Platform field for cross-platform compatibility

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
