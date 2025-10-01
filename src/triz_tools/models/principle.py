"""TRIZ Principle Models"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class TRIZPrinciple:
    """A TRIZ Inventive Principle"""
    principle_id: int
    principle_number: int
    principle_name: str
    description: str
    sub_principles: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    usage_frequency: str = "medium"
    innovation_level: int = 3
    related_principles: List[int] = field(default_factory=list)
    patent_references: List[str] = field(default_factory=list)

class TRIZKnowledgeBase:
    """Collection of TRIZ Principles"""
    def __init__(self):
        self.principles: Dict[int, TRIZPrinciple] = {}
        self._loaded = False

    def add_principle(self, principle: TRIZPrinciple):
        self.principles[principle.principle_id] = principle

    def get_principle(self, principle_id: int) -> Optional[TRIZPrinciple]:
        return self.principles.get(principle_id)

    def mark_loaded(self):
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded
