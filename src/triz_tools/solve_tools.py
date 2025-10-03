"""
TRIZ autonomous solve tools implementation.
Provides comprehensive problem analysis and solution generation.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict

from .models import (
    TRIZToolResponse,
    SolutionConcept,
    AnalysisReport,
    TRIZKnowledgeBase,
    ContradictionMatrix,
)
from .knowledge_base import (
    load_principles_from_file,
    load_contradiction_matrix,
)


# Load knowledge bases
PRINCIPLES = load_principles_from_file()
MATRIX = load_contradiction_matrix()


# TRIZ Parameter mapping for text analysis
PARAMETER_KEYWORDS = {
    1: ["weight", "mass", "heavy", "light"],
    2: ["stationary", "static", "fixed", "immobile"],
    3: ["length", "height", "width", "dimension"],
    4: ["area", "surface", "coverage"],
    5: ["volume", "capacity", "space"],
    6: ["speed", "velocity", "fast", "slow", "quick"],
    7: ["force", "strength", "pressure", "load"],
    8: ["stress", "strain", "tension", "compression"],
    9: ["shape", "form", "geometry", "configuration"],
    10: ["stability", "stable", "unstable", "equilibrium"],
    11: ["strength", "durability", "robust", "fragile"],
    12: ["rigidity", "stiffness", "flexible", "elastic"],
    13: ["damage", "wear", "deterioration", "erosion"],
    14: ["manufacturing", "production", "assembly", "fabrication"],
    15: ["durability", "lifetime", "longevity", "lifespan"],
    16: ["temperature", "heat", "cold", "thermal"],
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


def identify_parameters_from_text(text: str) -> List[int]:
    """
    Identify TRIZ parameters from problem description text.

    Args:
        text: Problem description

    Returns:
        List of parameter numbers found in text
    """
    text_lower = text.lower()
    identified_params = []

    for param_num, keywords in PARAMETER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                identified_params.append(param_num)
                break

    return list(set(identified_params))  # Remove duplicates


def extract_contradictions(problem_text: str) -> List[Dict[str, Any]]:
    """
    Extract technical contradictions from problem description.

    Args:
        problem_text: Problem description

    Returns:
        List of identified contradictions
    """
    contradictions = []
    seen_pairs = set()  # Track unique contradictions

    # Extended patterns for contradiction detection
    patterns = [
        # Standard patterns
        r"increase\s+(\w+(?:\s+\w+)?)\s+while\s+(?:reducing|decreasing)\s+(\w+(?:\s+\w+)?)",
        r"improve\s+(\w+(?:\s+\w+)?)\s+without\s+(?:increasing|adding)\s+(\w+(?:\s+\w+)?)",
        r"reduce\s+(\w+(?:\s+\w+)?)\s+while\s+(?:maintaining|keeping)\s+(\w+(?:\s+\w+)?)",
        r"decrease\s+(\w+(?:\s+\w+)?)\s+(?:from|to)\s+[\d.]+%?\s+to\s+[\d.]+%?",
        r"make\s+(?:more|less)\s+(\w+)\s+but\s+(?:not|without)\s+(\w+)",
        # New patterns for complex problems
        r"(\w+(?:\s+\w+)?)\s+by\s+\d+%\s+while\s+(\w+(?:\s+\w+)?)",
        r"more\s+(\w+)\s+to\s+handle.*instead",
        r"(\w+)\s+versus\s+(\w+)",
        r"(\w+)\s+vs\.?\s+(\w+)",
    ]

    text_lower = problem_text.lower()

    # Extract explicit contradictions
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if len(match) >= 2:
                improving = match[0]
                worsening = match[1] if len(match) > 1 else ""

                # Map to parameters
                improving_params = identify_parameters_from_text(improving)
                worsening_params = (
                    identify_parameters_from_text(worsening) if worsening else []
                )

                if improving_params and worsening_params:
                    for imp in improving_params:
                        for wor in worsening_params:
                            pair = (imp, wor)
                            if imp != wor and pair not in seen_pairs:
                                seen_pairs.add(pair)
                                contradictions.append(
                                    {
                                        "improving_parameter": imp,
                                        "worsening_parameter": wor,
                                        "parameter_names": {
                                            "improving": f"Parameter {imp}",
                                            "worsening": f"Parameter {wor}",
                                        },
                                    }
                                )

    # Look for specific contradictions in complex problems
    # Throughput vs Energy
    if "throughput" in text_lower and "energy" in text_lower:
        pair = (29, 18)  # Productivity vs Energy use
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            contradictions.append(
                {
                    "improving_parameter": 29,  # Productivity
                    "worsening_parameter": 18,  # Energy use by moving object
                    "parameter_names": {
                        "improving": "Productivity",
                        "worsening": "Energy consumption",
                    },
                }
            )

    # Quality vs Inspection
    if "quality" in text_lower and (
        "inspection" in text_lower or "defect" in text_lower
    ):
        pair = (28, 36)  # Accuracy vs Complexity
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            contradictions.append(
                {
                    "improving_parameter": 28,  # Measurement accuracy
                    "worsening_parameter": 36,  # Device complexity
                    "parameter_names": {
                        "improving": "Quality/Accuracy",
                        "worsening": "System complexity",
                    },
                }
            )

    # Flexibility vs Variants
    if "flexible" in text_lower or "variant" in text_lower:
        pair = (35, 36)  # Adaptability vs Complexity
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            contradictions.append(
                {
                    "improving_parameter": 35,  # Adaptability
                    "worsening_parameter": 36,  # Complexity
                    "parameter_names": {
                        "improving": "Adaptability",
                        "worsening": "System complexity",
                    },
                }
            )

    # Maintenance vs Downtime
    if "maintenance" in text_lower or "downtime" in text_lower:
        pair = (27, 25)  # Reliability vs Time
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            contradictions.append(
                {
                    "improving_parameter": 27,  # Reliability
                    "worsening_parameter": 25,  # Loss of time
                    "parameter_names": {
                        "improving": "Reliability",
                        "worsening": "Time loss",
                    },
                }
            )

    # If still no contradictions, use general approach
    if not contradictions:
        params = identify_parameters_from_text(problem_text)
        if len(params) >= 2:
            # Create potential contradictions from identified parameters
            for i in range(min(3, len(params) - 1)):
                pair = (params[i], params[i + 1])
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    contradictions.append(
                        {
                            "improving_parameter": params[i],
                            "worsening_parameter": params[i + 1],
                            "parameter_names": {
                                "improving": f"Parameter {params[i]}",
                                "worsening": f"Parameter {params[i + 1]}",
                            },
                        }
                    )

    return contradictions


def generate_ideal_final_result(problem_text: str) -> str:
    """
    Generate Ideal Final Result (IFR) statement.

    Args:
        problem_text: Problem description

    Returns:
        IFR statement
    """
    # Extract key goals and constraints
    goals = []
    constraints = []

    # Look for improvement goals
    improve_patterns = [
        r"reduce\s+(\w+(?:\s+\w+)*)",
        r"increase\s+(\w+(?:\s+\w+)*)",
        r"improve\s+(\w+(?:\s+\w+)*)",
        r"eliminate\s+(\w+(?:\s+\w+)*)",
        r"minimize\s+(\w+(?:\s+\w+)*)",
        r"maximize\s+(\w+(?:\s+\w+)*)",
    ]

    # Look for constraints
    constraint_patterns = [
        r"while\s+(?:maintaining|keeping)\s+(\w+(?:\s+\w+)*)",
        r"without\s+(?:increasing|adding|reducing)\s+(\w+(?:\s+\w+)*)",
        r"but\s+(?:not|without)\s+(\w+(?:\s+\w+)*)",
    ]

    text_lower = problem_text.lower()

    for pattern in improve_patterns:
        matches = re.findall(pattern, text_lower)
        goals.extend(matches)

    for pattern in constraint_patterns:
        matches = re.findall(pattern, text_lower)
        constraints.extend(matches)

    # Construct IFR
    ifr = "The ideal system would "

    if goals:
        ifr += f"achieve {', '.join(goals[:2])} "

    if constraints:
        ifr += f"while maintaining {', '.join(constraints[:2])} "

    ifr += "without adding complexity or cost to the system."

    return ifr


def select_top_principles(contradictions: List[Dict], problem_text: str) -> List[Dict]:
    """
    Select top TRIZ principles based on contradictions and problem context.

    Args:
        contradictions: List of identified contradictions
        problem_text: Original problem description

    Returns:
        List of top principles with scores
    """
    principle_scores = {}

    # Get principles from contradiction matrix
    for contradiction in contradictions:
        imp = contradiction["improving_parameter"]
        wor = contradiction["worsening_parameter"]

        # Get recommended principles from matrix
        result = MATRIX.lookup(imp, wor)
        if result:
            for principle_num in result.recommended_principles:
                if principle_num not in principle_scores:
                    principle_scores[principle_num] = 0
                principle_scores[principle_num] += 1.0

    # If no matrix matches, use common principles
    if not principle_scores:
        # Common universally applicable principles
        common_principles = [1, 2, 6, 10, 15, 25, 35]
        for p in common_principles:
            principle_scores[p] = 0.5

    # Sort by score and get top 5
    sorted_principles = sorted(
        principle_scores.items(), key=lambda x: x[1], reverse=True
    )[:5]

    # Format results
    top_principles = []
    for principle_id, score in sorted_principles:
        if principle_id in PRINCIPLES.principles:
            principle = PRINCIPLES.principles[principle_id]
            top_principles.append(
                {
                    "principle_id": principle_id,
                    "principle_name": principle.principle_name,
                    "relevance_score": min(score / 3.0, 1.0),  # Normalize score
                    "explanation": principle.description[:200] + "...",
                }
            )

    return top_principles


def generate_solution_concepts(
    problem_text: str, top_principles: List[Dict], contradictions: List[Dict]
) -> List[Dict]:
    """
    Generate solution concepts based on TRIZ principles.

    Args:
        problem_text: Original problem
        top_principles: Selected TRIZ principles
        contradictions: Identified contradictions

    Returns:
        List of solution concepts
    """
    concepts = []

    # Generate at least 3 concepts from top principles
    for i, principle_data in enumerate(top_principles[:3]):
        principle_id = principle_data["principle_id"]
        principle = PRINCIPLES.principles.get(principle_id)

        if not principle:
            continue

        # Create concept based on principle
        concept = {
            "concept_title": f"Solution using {principle.principle_name}",
            "description": f"Apply {principle.principle_name} principle to address the problem. "
            f"{principle.description} "
            f"This approach could help resolve the identified contradictions "
            f"by {principle.sub_principles[0] if principle.sub_principles else 'systematic innovation'}.",
            "applied_principles": [principle_id],
            "pros": [
                f"Directly addresses the contradiction",
                f"Based on proven TRIZ principle #{principle_id}",
                f"Can be implemented incrementally",
            ],
            "cons": [f"May require system redesign", f"Initial implementation cost"],
            "feasibility_score": 0.7
            + (0.05 * (3 - i)),  # Higher score for top principles
            "innovation_level": min(3 + i, 5),
        }

        concepts.append(concept)

    # Add a combined solution if we have multiple principles
    if len(top_principles) >= 2:
        combined_principles = [p["principle_id"] for p in top_principles[:2]]
        combined_names = [p["principle_name"] for p in top_principles[:2]]

        concepts.append(
            {
                "concept_title": f"Hybrid Solution: {' + '.join(combined_names)}",
                "description": f"Combine multiple TRIZ principles for a comprehensive solution. "
                f"By integrating {combined_names[0]} with {combined_names[1]}, "
                f"we can address multiple aspects of the problem simultaneously. "
                f"This hybrid approach leverages synergies between different inventive principles.",
                "applied_principles": combined_principles,
                "pros": [
                    "Addresses multiple contradictions",
                    "Synergistic effects possible",
                    "More robust solution",
                    "Higher innovation potential",
                ],
                "cons": [
                    "More complex implementation",
                    "Higher initial investment",
                    "Requires careful integration",
                ],
                "feasibility_score": 0.65,
                "innovation_level": 4,
            }
        )

    return concepts


def triz_solve_autonomous(
    problem_description: str, context: Optional[Dict[str, Any]] = None
) -> TRIZToolResponse:
    """
    Perform autonomous TRIZ analysis and solution generation using DeepResearchAgent.

    This function performs genius-level multi-stage research across all knowledge sources
    to generate deeply informed solutions with research provenance.

    Args:
        problem_description: Detailed problem description
        context: Optional context information (industry, constraints, etc.)

    Returns:
        TRIZToolResponse with complete research-based analysis and solutions
    """
    # Validate input
    if not problem_description or len(problem_description.strip()) < 10:
        return TRIZToolResponse(
            success=False,
            message="Problem description is empty or insufficient. Please provide more detailed information.",
            data={},
        )

    try:
        # Use DeepResearchAgent for genius-level research
        from .research_agent import get_research_agent

        research_agent = get_research_agent()
        research_report = research_agent.research_problem(problem_description)

        # Create problem summary
        problem_summary = problem_description[:200].strip()
        if len(problem_description) > 200:
            problem_summary += "..."

        # Generate IFR (simplified for backward compatibility)
        ifr = generate_ideal_final_result(problem_description)

        # Format contradictions for response
        contradictions_formatted = [
            {
                "description": c.get("description", "N/A"),
                "type": c.get("type", "technical"),
                "improving": c.get("improving", "N/A"),
                "worsening": c.get("worsening", "N/A"),
                "source": c.get("source", "analysis"),
            }
            for c in research_report.contradictions
        ]

        # Format principles with rich research data
        principles_formatted = [
            {
                "number": p.get("id"),
                "name": p.get("name"),
                "description": p.get("description"),
                "relevance_score": p.get("score", 0.5),
                "sources": p.get("sources", []),
                "sub_principles": p.get("sub_principles", []),
                "examples": p.get("examples", []),
                "domains": p.get("domains", []),
                "usage_frequency": p.get("usage_frequency", "medium"),
                "innovation_level": p.get("innovation_level", 3),
            }
            for p in research_report.principles
        ]

        # Format solutions with full research provenance
        solutions_formatted = [
            {
                "title": s.get("title"),
                "description": s.get("description"),
                "principle": s.get("applied_principles", []),
                "principle_names": s.get("principle_names", []),
                "research_support": s.get("research_support", []),
                "cross_domain_insights": s.get("cross_domain_insights", []),
                "pros": s.get("pros", []),
                "cons": s.get("cons", []),
                "feasibility_score": s.get("feasibility_score", 0.7),
                "confidence": s.get("confidence", 0.5),
                "implementation_hints": s.get("implementation_hints", []),
                "citations": s.get("citations", []),
            }
            for s in research_report.solutions
        ]

        # Extract materials recommendations from findings
        materials_recommendations = []
        for finding in research_report.findings:
            # Check if finding is from materials sources
            source = finding.source.lower()
            if "materials" in source or "composite" in source or "polymer" in source:
                # Extract clean content text (use full chunk - we have 8000 char chunks)
                content = finding.content
                if isinstance(content, str):
                    reasoning = content[:5000]  # Show substantial content
                elif isinstance(content, dict):
                    # Try to get text from dict
                    reasoning = content.get(
                        "content", content.get("full_content", str(content))
                    )[:5000]
                else:
                    reasoning = str(content)[:5000]

                # Extract book name for better naming
                book_name = (
                    source.split("(")[1].split(")")[0] if "(" in source else "Research"
                )

                material_info = {
                    "name": f"Material guidance from {book_name[:30]}",
                    "source": finding.source,
                    "reasoning": reasoning,
                    "relevance_score": finding.relevance_score,
                    "category": finding.metadata.get("category", "Materials"),
                }
                materials_recommendations.append(material_info)

        # Sort by relevance
        materials_recommendations.sort(
            key=lambda x: x.get("relevance_score", 0), reverse=True
        )
        materials_recommendations = materials_recommendations[:5]  # Top 5

        # Compile comprehensive analysis report
        analysis_data = {
            "problem_summary": problem_summary,
            "ideal_final_result": ifr,
            "contradictions": contradictions_formatted,
            "recommended_principles": principles_formatted,
            "solutions": solutions_formatted,
            "cross_domain_analogies": research_report.cross_domain_analogies,
            "confidence_score": research_report.confidence_score,
            "research_depth": {
                "total_findings": len(research_report.findings),
                "sources_consulted": len(
                    set(f.source for f in research_report.findings)
                ),
                "queries_executed": len(research_report.research_queries),
                "knowledge_gaps": research_report.knowledge_gaps,
            },
            "materials_recommendations": materials_recommendations,
        }

        return TRIZToolResponse(
            success=True,
            message=f"Deep research completed: {len(research_report.findings)} findings from {len(set(f.source for f in research_report.findings))} sources",
            data=analysis_data,
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()

        # Log the error
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error during deep research: {str(e)}\n{error_details}")

        # Fallback to simple analysis
        try:
            # Use legacy simple analysis as fallback
            contradictions = extract_contradictions(problem_description)
            ifr = generate_ideal_final_result(problem_description)
            top_principles = select_top_principles(contradictions, problem_description)
            solution_concepts = generate_solution_concepts(
                problem_description, top_principles, contradictions
            )

            analysis_data = {
                "problem_summary": problem_description[:200],
                "ideal_final_result": ifr,
                "contradictions": contradictions,
                "recommended_principles": top_principles,
                "solutions": solution_concepts,
                "confidence_score": 0.6,
                "fallback_mode": True,
                "error_message": f"Deep research failed, using fallback: {str(e)}",
            }

            return TRIZToolResponse(
                success=True,
                message="TRIZ analysis completed (fallback mode)",
                data=analysis_data,
            )
        except Exception as fallback_error:
            return TRIZToolResponse(
                success=False,
                message=f"Error during TRIZ analysis: {str(e)}. Fallback also failed: {str(fallback_error)}",
                data={},
            )


def triz_solve_with_context(
    problem_description: str, context: Dict[str, Any]
) -> TRIZToolResponse:
    """
    Solve TRIZ problem with additional context.
    This is an alias for triz_solve_autonomous with context.

    Args:
        problem_description: Problem description
        context: Additional context (industry, constraints, etc.)

    Returns:
        TRIZToolResponse with analysis
    """
    return triz_solve_autonomous(problem_description, context=context)


def triz_solve_iterative(
    problem_description: str,
    previous_solutions: Optional[List[Dict[str, Any]]] = None,
    max_iterations: int = 3,
) -> TRIZToolResponse:
    """
    Iteratively solve TRIZ problem, refining solutions.

    Args:
        problem_description: Problem description
        previous_solutions: Previously generated solutions to refine
        max_iterations: Maximum iterations

    Returns:
        TRIZToolResponse with refined analysis
    """
    # For now, just call autonomous solve
    # Can be enhanced later to use previous_solutions for refinement
    return triz_solve_autonomous(problem_description)
