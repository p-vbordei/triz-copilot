"""Session Models"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime
from pathlib import Path
import json

if TYPE_CHECKING:
    from .response import WorkflowStage, WorkflowType


class SessionData:
    """Session data container for workflow state"""
    def __init__(self):
        self.problem_statement: str = ""
        self.ideal_final_result: str = ""
        self.contradictions: List[Dict[str, Any]] = []
        self.principles: List[int] = []
        self.solutions: List[Dict[str, Any]] = []


@dataclass
class ProblemSession:
    """TRIZ problem-solving session"""
    session_id: str
    problem_statement: str = ""
    stage: str = "problem_definition"
    current_stage: Optional["WorkflowStage"] = None
    workflow_type: Optional["WorkflowType"] = None
    user_inputs: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    platform: str = "gemini"  # Platform field for cross-platform compatibility

    def __post_init__(self):
        # Import here to avoid circular imports
        from .response import WorkflowStage, WorkflowType

        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        # Set current_stage from stage if not provided
        if self.current_stage is None and self.stage:
            try:
                self.current_stage = WorkflowStage(self.stage)
            except ValueError:
                self.current_stage = WorkflowStage.PROBLEM_DEFINITION
        # Default workflow type if not set
        if self.workflow_type is None:
            self.workflow_type = WorkflowType.GUIDED
        # Initialize session_data if not exists
        if not hasattr(self, '_session_data'):
            self._session_data = SessionData()

    @property
    def session_data(self) -> SessionData:
        """Get session data"""
        if not hasattr(self, '_session_data'):
            self._session_data = SessionData()
        return self._session_data

    def save_to_file(self, directory: Path) -> Path:
        """Save session to JSON file"""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.session_id}.json"

        # Convert to dict for JSON serialization
        data = asdict(self)
        # Convert enums and datetime to strings
        if self.current_stage:
            data['current_stage'] = self.current_stage.value
        if self.workflow_type:
            data['workflow_type'] = self.workflow_type.value
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        return file_path

    @classmethod
    def load_from_file(cls, file_path: Path) -> "ProblemSession":
        """Load session from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Convert datetime strings back
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])

        return cls(**data)

    def add_user_response(self, key: str, value: Any):
        """Add user response to session"""
        self.user_inputs[key] = value
        self.updated_at = datetime.now()

    def reset(self):
        """Reset session to initial state"""
        from .response import WorkflowStage, WorkflowType
        self.current_stage = WorkflowStage.PROBLEM_DEFINITION
        self.problem_statement = ""
        self.user_inputs = {}
        self.analysis_results = {}
        self._session_data = SessionData()
        self.updated_at = datetime.now()

    def advance_stage(self):
        """Advance to next workflow stage"""
        from .response import WorkflowStage

        stage_order = [
            WorkflowStage.PROBLEM_DEFINITION,
            WorkflowStage.CONTRADICTION_ANALYSIS,
            WorkflowStage.PRINCIPLE_SELECTION,
            WorkflowStage.SOLUTION_GENERATION,
            WorkflowStage.EVALUATION,
            WorkflowStage.COMPLETED
        ]

        try:
            current_index = stage_order.index(self.current_stage)
            if current_index < len(stage_order) - 1:
                self.current_stage = stage_order[current_index + 1]
                self.stage = self.current_stage.value
                self.updated_at = datetime.now()
        except (ValueError, IndexError):
            pass  # Stay at current stage if can't advance
