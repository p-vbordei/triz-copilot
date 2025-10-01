"""
Problem Session Model (T024)
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .response import WorkflowStage, WorkflowType


@dataclass
class SessionData:
    """Session-specific data for workflow stages"""
    problem_statement: str = ""
    system_description: str = ""
    ideal_final_result: str = ""
    useful_functions: List[str] = field(default_factory=list)
    harmful_functions: List[str] = field(default_factory=list)
    contradictions: List[Dict] = field(default_factory=list)
    selected_principles: List[int] = field(default_factory=list)
    solution_concepts: List[Dict] = field(default_factory=list)
    evaluation_results: Dict[str, Any] = field(default_factory=dict)
    user_responses: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ProblemSession:
    """Represents a TRIZ problem-solving session"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    workflow_type: WorkflowType = WorkflowType.GUIDED
    current_stage: WorkflowStage = WorkflowStage.PROBLEM_DEFINITION
    session_data: SessionData = field(default_factory=SessionData)
    completed: bool = False
    platform: str = "gemini"  # TASK-025: Platform field for Claude/Gemini compatibility
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def advance_stage(self) -> bool:
        """Move to next workflow stage"""
        stage_order = [
            WorkflowStage.PROBLEM_DEFINITION,
            WorkflowStage.CONTRADICTION_ANALYSIS,
            WorkflowStage.PRINCIPLE_SELECTION,
            WorkflowStage.SOLUTION_GENERATION,
            WorkflowStage.EVALUATION,
            WorkflowStage.COMPLETED,
        ]
        
        try:
            current_index = stage_order.index(self.current_stage)
            if current_index < len(stage_order) - 1:
                self.current_stage = stage_order[current_index + 1]
                self.update_activity()
                if self.current_stage == WorkflowStage.COMPLETED:
                    self.completed = True
                return True
        except (ValueError, IndexError):
            pass
        return False
    
    def reset(self) -> None:
        """Reset session to initial state"""
        self.current_stage = WorkflowStage.PROBLEM_DEFINITION
        self.session_data = SessionData()
        self.completed = False
        self.update_activity()
    
    def add_user_response(self, stage: str, response: str) -> None:
        """Add user response for a stage"""
        self.session_data.user_responses.append({
            "stage": stage,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        self.update_activity()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "workflow_type": self.workflow_type.value,
            "current_stage": self.current_stage.value,
            "session_data": asdict(self.session_data),
            "completed": self.completed,
            "platform": self.platform,  # TASK-025: Include platform in serialization
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProblemSession":
        """Create session from dictionary"""
        session = cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            workflow_type=WorkflowType(data["workflow_type"]),
            current_stage=WorkflowStage(data["current_stage"]),
            completed=data.get("completed", False),
            platform=data.get("platform", "gemini"),  # TASK-025: Default to gemini for backward compatibility
        )
        
        # Restore session data
        session_data = SessionData(**data["session_data"])
        session.session_data = session_data
        
        return session
    
    def save_to_file(self, directory: Path) -> None:
        """Save session to JSON file"""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.session_id}.json"
        
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> Optional["ProblemSession"]:
        """Load session from JSON file"""
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None