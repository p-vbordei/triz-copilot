"""
Analysis Report Model (T027)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid


@dataclass
class AnalysisReport:
    """Structured output containing complete TRIZ analysis results"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)
    report_type: str = "autonomous_solve"  # workflow_summary, autonomous_solve, tool_analysis
    problem_summary: str = ""
    ideal_final_result: str = ""
    contradictions_identified: List[Dict[str, Any]] = field(default_factory=list)
    contradiction_analysis: Dict[str, Any] = field(default_factory=dict)
    top_principles: List[Dict[str, Any]] = field(default_factory=list)
    principle_rationale: Dict[int, str] = field(default_factory=dict)
    solution_concepts: List[Dict[str, Any]] = field(default_factory=list)
    evaluation_matrix: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    materials_analysis: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    confidence_score: float = 0.7
    
    def add_contradiction(
        self,
        improving_param: int,
        worsening_param: int,
        param_names: Dict[str, str],
        confidence: float = 0.7
    ) -> None:
        """Add identified contradiction"""
        contradiction = {
            "improving_parameter": improving_param,
            "worsening_parameter": worsening_param,
            "parameter_names": param_names,
            "confidence": confidence,
        }
        self.contradictions_identified.append(contradiction)
    
    def add_principle_recommendation(
        self,
        principle_id: int,
        principle_name: str,
        relevance_score: float,
        explanation: str
    ) -> None:
        """Add recommended principle"""
        principle = {
            "principle_id": principle_id,
            "principle_name": principle_name,
            "relevance_score": relevance_score,
            "explanation": explanation,
        }
        self.top_principles.append(principle)
        self.principle_rationale[principle_id] = explanation
    
    def add_solution_concept(self, concept: Dict[str, Any]) -> None:
        """Add solution concept to report"""
        self.solution_concepts.append(concept)
    
    def add_material_recommendation(
        self,
        material_name: str,
        properties: Dict[str, Any],
        advantages: List[str],
        disadvantages: List[str],
        cost_index: float
    ) -> None:
        """Add material recommendation"""
        if "recommendations" not in self.materials_analysis:
            self.materials_analysis["recommendations"] = []
        
        material = {
            "material_name": material_name,
            "properties": properties,
            "advantages": advantages,
            "disadvantages": disadvantages,
            "cost_index": cost_index,
        }
        self.materials_analysis["recommendations"].append(material)
    
    def set_evaluation_matrix(
        self,
        criteria: List[str],
        weights: Dict[str, float],
        scores: Dict[str, Dict[str, float]]
    ) -> None:
        """Set solution evaluation matrix"""
        self.evaluation_matrix = {
            "criteria": criteria,
            "weights": weights,
            "scores": scores,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "generated_at": self.generated_at.isoformat(),
            "report_type": self.report_type,
            "problem_summary": self.problem_summary,
            "ideal_final_result": self.ideal_final_result,
            "contradictions_identified": self.contradictions_identified,
            "contradiction_analysis": self.contradiction_analysis,
            "top_principles": self.top_principles,
            "principle_rationale": self.principle_rationale,
            "solution_concepts": self.solution_concepts,
            "evaluation_matrix": self.evaluation_matrix,
            "recommendations": self.recommendations,
            "materials_analysis": self.materials_analysis,
            "next_steps": self.next_steps,
            "confidence_score": self.confidence_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisReport":
        """Create from dictionary"""
        report = cls()
        for key, value in data.items():
            if key == "generated_at":
                setattr(report, key, datetime.fromisoformat(value))
            else:
                setattr(report, key, value)
        return report
    
    def generate_summary(self) -> str:
        """Generate text summary of report"""
        summary = f"""
TRIZ Analysis Report
====================
Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M')}
Type: {self.report_type}
Confidence: {self.confidence_score:.1%}

Problem Summary:
{self.problem_summary}

Ideal Final Result:
{self.ideal_final_result}

Contradictions Identified: {len(self.contradictions_identified)}
Top Principles: {len(self.top_principles)}
Solution Concepts: {len(self.solution_concepts)}

Recommendations:
"""
        for i, rec in enumerate(self.recommendations, 1):
            summary += f"{i}. {rec}\n"
        
        return summary