"""
TRIZ Analysis Service (T031)
Core service for TRIZ problem analysis and solution generation.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re

from ..models import (
    TRIZKnowledgeBase,
    ContradictionMatrix,
    SolutionConcept,
    AnalysisReport,
)
from ..knowledge_base import (
    load_principles_from_file,
    load_contradiction_matrix,
)

logger = logging.getLogger(__name__)


@dataclass
class AnalysisContext:
    """Context for TRIZ analysis"""
    problem_statement: str
    industry: Optional[str] = None
    constraints: List[str] = None
    priority: Optional[str] = None
    existing_solutions: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.existing_solutions is None:
            self.existing_solutions = []


class TRIZAnalysisService:
    """Service for performing TRIZ analysis"""
    
    def __init__(self):
        """Initialize analysis service"""
        self.principles = load_principles_from_file()
        self.matrix = load_contradiction_matrix()
        
        # Parameter keyword mappings
        self.parameter_keywords = self._load_parameter_keywords()
        
        logger.info("TRIZ Analysis Service initialized")
    
    def _load_parameter_keywords(self) -> Dict[int, List[str]]:
        """Load keyword mappings for parameters"""
        return {
            1: ["weight", "mass", "heavy", "light", "lightweight"],
            2: ["stationary", "static", "fixed", "immobile"],
            3: ["length", "height", "width", "dimension", "size"],
            4: ["area", "surface", "coverage", "footprint"],
            5: ["volume", "capacity", "space", "size"],
            6: ["speed", "velocity", "fast", "slow", "quick", "rapid"],
            7: ["force", "strength", "pressure", "load", "stress"],
            8: ["stress", "strain", "tension", "compression"],
            9: ["shape", "form", "geometry", "configuration"],
            10: ["stability", "stable", "unstable", "equilibrium", "balance"],
            11: ["strength", "durability", "robust", "fragile", "tough"],
            12: ["rigidity", "stiffness", "flexible", "elastic"],
            13: ["damage", "wear", "deterioration", "erosion", "degradation"],
            14: ["manufacturing", "production", "assembly", "fabrication"],
            15: ["durability", "lifetime", "longevity", "lifespan"],
            16: ["temperature", "heat", "cold", "thermal", "cooling", "heating"],
            17: ["brightness", "illumination", "light", "luminosity"],
            18: ["energy", "power", "consumption", "efficiency"],
            19: ["motion", "movement", "kinetic", "dynamic"],
            20: ["stationary", "static", "fixed", "immobile"],
            21: ["power", "energy", "wattage", "horsepower"],
            22: ["waste", "loss", "inefficiency", "surplus"],
            23: ["harmful", "damaging", "negative", "adverse"],
            24: ["information", "data", "signal", "communication"],
            25: ["time", "duration", "period", "interval"],
            26: ["quantity", "amount", "number", "count"],
            27: ["reliability", "dependable", "consistent", "failure"],
            28: ["accuracy", "precision", "exact", "error"],
            29: ["productivity", "throughput", "output", "efficiency"],
            30: ["external", "outside", "environmental", "surrounding"],
            31: ["side effect", "unintended", "collateral", "byproduct"],
            32: ["manufacturability", "producibility", "ease of making"],
            33: ["convenience", "usability", "user-friendly", "ease"],
            34: ["repair", "maintenance", "service", "fix"],
            35: ["adaptability", "flexible", "versatile", "adjustable"],
            36: ["complexity", "complicated", "simple", "intricate"],
            37: ["control", "monitor", "regulate", "manage"],
            38: ["automation", "automatic", "manual", "human"],
            39: ["productivity", "efficiency", "output", "performance"],
        }
    
    def analyze_problem(
        self,
        context: AnalysisContext
    ) -> AnalysisReport:
        """
        Perform complete TRIZ analysis.
        
        Args:
            context: Analysis context with problem details
        
        Returns:
            Complete analysis report
        """
        # 1. Extract contradictions
        contradictions = self.identify_contradictions(context.problem_statement)
        
        # 2. Generate IFR
        ifr = self.generate_ideal_final_result(context.problem_statement)
        
        # 3. Find relevant principles
        principles = self.find_relevant_principles(
            contradictions,
            context.problem_statement
        )
        
        # 4. Generate solution concepts
        concepts = self.generate_solution_concepts(
            principles[:5],  # Top 5 principles
            context
        )
        
        # 5. Create implementation plan
        plan = self.create_implementation_plan(concepts, context)
        
        # 6. Estimate impact
        impact = self.estimate_impact(concepts)
        
        # Create report
        report = AnalysisReport(
            problem_statement=context.problem_statement,
            contradictions=contradictions,
            recommended_principles=[p["id"] for p in principles[:10]],
            solution_concepts=concepts,
            implementation_plan=plan,
            estimated_impact=impact
        )
        
        return report
    
    def identify_contradictions(
        self,
        problem_text: str
    ) -> List[Dict[str, Any]]:
        """
        Identify technical contradictions in problem.
        
        Args:
            problem_text: Problem description
        
        Returns:
            List of identified contradictions
        """
        contradictions = []
        text_lower = problem_text.lower()
        
        # Pattern matching for contradictions
        patterns = [
            (r"increase\s+(\w+)\s+while\s+(?:reducing|decreasing)\s+(\w+)", "technical"),
            (r"improve\s+(\w+)\s+without\s+(?:increasing|adding)\s+(\w+)", "technical"),
            (r"reduce\s+(\w+)\s+while\s+(?:maintaining|keeping)\s+(\w+)", "technical"),
            (r"make\s+(?:more|less)\s+(\w+)\s+but\s+(?:not|without)\s+(\w+)", "technical"),
            (r"both\s+(\w+)\s+and\s+(\w+)", "physical"),
        ]
        
        for pattern, cont_type in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match) >= 2:
                    # Map to parameters
                    imp_params = self._text_to_parameters(match[0])
                    wor_params = self._text_to_parameters(match[1])
                    
                    for imp in imp_params:
                        for wor in wor_params:
                            if imp != wor:
                                contradictions.append({
                                    "type": cont_type,
                                    "improving_parameter": imp,
                                    "worsening_parameter": wor,
                                    "description": f"{match[0]} vs {match[1]}"
                                })
        
        return contradictions
    
    def _text_to_parameters(self, text: str) -> List[int]:
        """Convert text to parameter numbers"""
        params = []
        text_lower = text.lower()
        
        for param_num, keywords in self.parameter_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    params.append(param_num)
                    break
        
        return params if params else [1]  # Default to weight if no match
    
    def generate_ideal_final_result(self, problem_text: str) -> str:
        """
        Generate IFR statement.
        
        Args:
            problem_text: Problem description
        
        Returns:
            IFR statement
        """
        # Extract key goals
        goals = []
        constraints = []
        
        goal_patterns = [
            r"reduce\s+(\w+(?:\s+\w+)*)",
            r"increase\s+(\w+(?:\s+\w+)*)",
            r"improve\s+(\w+(?:\s+\w+)*)",
            r"eliminate\s+(\w+(?:\s+\w+)*)",
        ]
        
        constraint_patterns = [
            r"while\s+(?:maintaining|keeping)\s+(\w+(?:\s+\w+)*)",
            r"without\s+(?:increasing|adding)\s+(\w+(?:\s+\w+)*)",
        ]
        
        text_lower = problem_text.lower()
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, text_lower)
            goals.extend(matches[:2])
        
        for pattern in constraint_patterns:
            matches = re.findall(pattern, text_lower)
            constraints.extend(matches[:2])
        
        # Construct IFR
        ifr = "The ideal system would "
        
        if goals:
            ifr += f"achieve {', '.join(goals[:2])} "
        
        if constraints:
            ifr += f"while maintaining {', '.join(constraints[:2])} "
        
        ifr += "by itself, without additional resources or complexity."
        
        return ifr
    
    def find_relevant_principles(
        self,
        contradictions: List[Dict[str, Any]],
        problem_text: str
    ) -> List[Dict[str, Any]]:
        """
        Find relevant TRIZ principles.
        
        Args:
            contradictions: Identified contradictions
            problem_text: Problem description
        
        Returns:
            Ranked list of principles
        """
        principle_scores = {}
        
        # Score from contradiction matrix
        for contradiction in contradictions:
            imp = contradiction["improving_parameter"]
            wor = contradiction["worsening_parameter"]
            
            result = self.matrix.lookup(imp, wor)
            if result:
                for principle_num in result.recommended_principles:
                    if principle_num not in principle_scores:
                        principle_scores[principle_num] = 0
                    principle_scores[principle_num] += 1.0
        
        # Add common principles if no matches
        if not principle_scores:
            common = [1, 2, 6, 10, 15, 25, 35]
            for p in common:
                principle_scores[p] = 0.5
        
        # Sort and format
        sorted_principles = sorted(
            principle_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        results = []
        for principle_id, score in sorted_principles:
            if principle_id in self.principles.principles:
                principle = self.principles.principles[principle_id]
                results.append({
                    "id": principle_id,
                    "name": principle.principle_name,
                    "description": principle.description,
                    "score": min(score / 3.0, 1.0),
                    "sub_principles": principle.sub_principles[:3]
                })
        
        return results
    
    def generate_solution_concepts(
        self,
        principles: List[Dict[str, Any]],
        context: AnalysisContext
    ) -> List[SolutionConcept]:
        """
        Generate solution concepts.
        
        Args:
            principles: Selected principles
            context: Analysis context
        
        Returns:
            List of solution concepts
        """
        concepts = []
        
        for i, principle_data in enumerate(principles[:3]):
            concept = SolutionConcept(
                concept_title=f"Apply {principle_data['name']}",
                description=self._generate_concept_description(
                    principle_data,
                    context
                ),
                applied_principles=[principle_data['id']],
                pros=self._generate_pros(principle_data),
                cons=self._generate_cons(principle_data),
                feasibility_score=0.7 + (0.05 * (3 - i)),
                innovation_level=min(3 + i, 5)
            )
            concepts.append(concept)
        
        # Add hybrid concept
        if len(principles) >= 2:
            hybrid = SolutionConcept(
                concept_title=f"Hybrid: {principles[0]['name']} + {principles[1]['name']}",
                description=f"Combine {principles[0]['name']} with {principles[1]['name']} "
                           f"for synergistic effects. {principles[0]['description'][:100]}... "
                           f"integrated with {principles[1]['description'][:100]}...",
                applied_principles=[principles[0]['id'], principles[1]['id']],
                pros=[
                    "Addresses multiple contradictions",
                    "Synergistic effects",
                    "More comprehensive solution"
                ],
                cons=[
                    "Higher complexity",
                    "Requires careful integration"
                ],
                feasibility_score=0.65,
                innovation_level=4
            )
            concepts.append(hybrid)
        
        return concepts
    
    def _generate_concept_description(
        self,
        principle: Dict[str, Any],
        context: AnalysisContext
    ) -> str:
        """Generate concept description"""
        desc = f"Apply the {principle['name']} principle to {context.problem_statement[:100]}. "
        desc += f"{principle['description'][:200]}... "
        
        if principle.get('sub_principles'):
            desc += f"Specifically: {principle['sub_principles'][0]}"
        
        return desc
    
    def _generate_pros(self, principle: Dict[str, Any]) -> List[str]:
        """Generate pros for a principle"""
        return [
            f"Based on proven TRIZ principle #{principle['id']}",
            "Addresses core contradiction",
            "Can be implemented incrementally",
            f"High success rate in {principle.get('domains', ['engineering'])[0]}"
        ]
    
    def _generate_cons(self, principle: Dict[str, Any]) -> List[str]:
        """Generate cons for a principle"""
        return [
            "May require system redesign",
            "Initial implementation cost",
            "Training may be required"
        ]
    
    def create_implementation_plan(
        self,
        concepts: List[SolutionConcept],
        context: AnalysisContext
    ) -> Dict[str, Any]:
        """
        Create implementation plan.
        
        Args:
            concepts: Solution concepts
            context: Analysis context
        
        Returns:
            Implementation plan
        """
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Evaluation",
                    "duration": "2 weeks",
                    "tasks": [
                        "Detailed feasibility analysis",
                        "Cost-benefit analysis",
                        "Risk assessment"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Prototype",
                    "duration": "4 weeks",
                    "tasks": [
                        "Design prototype",
                        "Build test version",
                        "Initial testing"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Implementation",
                    "duration": "8 weeks",
                    "tasks": [
                        "Full implementation",
                        "Integration testing",
                        "Deployment"
                    ]
                }
            ],
            "resources": [
                "Engineering team",
                "Testing facilities",
                "Budget allocation"
            ],
            "risks": [
                "Technical complexity",
                "Integration challenges",
                "Change management"
            ]
        }
    
    def estimate_impact(
        self,
        concepts: List[SolutionConcept]
    ) -> Dict[str, float]:
        """
        Estimate solution impact.
        
        Args:
            concepts: Solution concepts
        
        Returns:
            Impact estimates
        """
        if not concepts:
            return {}
        
        # Average scores
        avg_feasibility = sum(c.feasibility_score for c in concepts) / len(concepts)
        avg_innovation = sum(c.innovation_level for c in concepts) / len(concepts)
        
        return {
            "feasibility": avg_feasibility,
            "innovation": avg_innovation / 5.0,
            "risk_level": 1.0 - avg_feasibility,
            "potential_improvement": min(avg_feasibility * 1.5, 0.9),
            "implementation_complexity": avg_innovation / 5.0
        }


# Singleton instance
_analysis_service: Optional[TRIZAnalysisService] = None


def get_analysis_service(reset: bool = False) -> TRIZAnalysisService:
    """Get or create analysis service singleton"""
    global _analysis_service
    
    if reset or _analysis_service is None:
        _analysis_service = TRIZAnalysisService()
    
    return _analysis_service