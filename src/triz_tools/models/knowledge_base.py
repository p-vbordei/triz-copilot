"""
TRIZ Knowledge Base Model (T022)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np


@dataclass
class TRIZPrinciple:
    """Individual TRIZ Inventive Principle"""
    principle_id: int
    principle_number: int
    principle_name: str
    description: str
    sub_principles: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    patent_references: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    contradiction_params: List[int] = field(default_factory=list)
    usage_frequency: str = "medium"  # high, medium, low
    innovation_level: int = 3  # 1-5
    related_principles: List[int] = field(default_factory=list)
    embedding_vector: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/serialization"""
        return {
            "principle_id": self.principle_id,
            "principle_number": self.principle_number,
            "principle_name": self.principle_name,
            "description": self.description,
            "sub_principles": self.sub_principles,
            "examples": self.examples,
            "patent_references": self.patent_references,
            "domains": self.domains,
            "contradiction_params": self.contradiction_params,
            "usage_frequency": self.usage_frequency,
            "innovation_level": self.innovation_level,
            "related_principles": self.related_principles,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TRIZPrinciple":
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k != "embedding_vector"})


class TRIZKnowledgeBase:
    """Repository of all TRIZ Inventive Principles"""
    
    def __init__(self):
        self.principles: Dict[int, TRIZPrinciple] = {}
        self._loaded = False
    
    def add_principle(self, principle: TRIZPrinciple) -> None:
        """Add a principle to the knowledge base"""
        self.principles[principle.principle_id] = principle
    
    def get_principle(self, principle_id: int) -> Optional[TRIZPrinciple]:
        """Get a principle by ID"""
        return self.principles.get(principle_id)
    
    def get_all_principles(self) -> List[TRIZPrinciple]:
        """Get all principles"""
        return list(self.principles.values())
    
    def search_by_domain(self, domain: str) -> List[TRIZPrinciple]:
        """Find principles applicable to a domain"""
        results = []
        for principle in self.principles.values():
            if domain.lower() in [d.lower() for d in principle.domains]:
                results.append(principle)
        return results
    
    def get_related_principles(self, principle_id: int) -> List[TRIZPrinciple]:
        """Get principles related to a given principle"""
        principle = self.get_principle(principle_id)
        if not principle:
            return []
        
        related = []
        for related_id in principle.related_principles:
            if related_principle := self.get_principle(related_id):
                related.append(related_principle)
        return related
    
    def is_loaded(self) -> bool:
        """Check if knowledge base is loaded"""
        return self._loaded and len(self.principles) > 0
    
    def mark_loaded(self) -> None:
        """Mark knowledge base as loaded"""
        self._loaded = True