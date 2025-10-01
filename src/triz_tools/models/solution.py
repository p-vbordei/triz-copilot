"""
Solution Concept Model (T025)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class SolutionConcept:
    """Generated solution with applied principles and evaluation"""
    solution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    concept_title: str = ""
    description: str = ""
    applied_principles: List[int] = field(default_factory=list)
    principle_applications: Dict[int, str] = field(default_factory=dict)
    innovation_level: int = 3  # 1-5
    feasibility_score: float = 0.5  # 0.0-1.0
    effectiveness_score: float = 0.5  # 0.0-1.0
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    materials_suggested: List[str] = field(default_factory=list)
    implementation_steps: List[str] = field(default_factory=list)
    patents_to_review: List[str] = field(default_factory=list)
    estimated_cost: str = "medium"  # low, medium, high
    development_time: str = "medium"  # short, medium, long
    
    def validate(self) -> bool:
        """Validate solution concept data"""
        if not self.concept_title or not self.description:
            return False
        if not self.applied_principles:
            return False
        if not (0.0 <= self.feasibility_score <= 1.0):
            return False
        if not (0.0 <= self.effectiveness_score <= 1.0):
            return False
        if not (1 <= self.innovation_level <= 5):
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "solution_id": self.solution_id,
            "session_id": self.session_id,
            "concept_title": self.concept_title,
            "description": self.description,
            "applied_principles": self.applied_principles,
            "principle_applications": self.principle_applications,
            "innovation_level": self.innovation_level,
            "feasibility_score": self.feasibility_score,
            "effectiveness_score": self.effectiveness_score,
            "pros": self.pros,
            "cons": self.cons,
            "materials_suggested": self.materials_suggested,
            "implementation_steps": self.implementation_steps,
            "patents_to_review": self.patents_to_review,
            "estimated_cost": self.estimated_cost,
            "development_time": self.development_time,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolutionConcept":
        """Create from dictionary"""
        return cls(**data)
    
    def add_principle_application(self, principle_id: int, application: str) -> None:
        """Add how a principle was applied"""
        if principle_id not in self.applied_principles:
            self.applied_principles.append(principle_id)
        self.principle_applications[principle_id] = application
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        # Weighted combination of scores
        weights = {
            "feasibility": 0.35,
            "effectiveness": 0.35,
            "innovation": 0.30,
        }
        
        innovation_normalized = self.innovation_level / 5.0
        
        score = (
            weights["feasibility"] * self.feasibility_score +
            weights["effectiveness"] * self.effectiveness_score +
            weights["innovation"] * innovation_normalized
        )
        
        return round(score, 2)