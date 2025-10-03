"""
PHASE 3: FUNCTION ANALYSIS & CONTRADICTIONS (Steps 17-26)

Deep dive into Subject-Action-Object relationships.
Map ALL functions: Useful, Insufficient, Excessive, Harmful.
Identify Technical and Physical Contradictions.

Steps:
17. Map all Subject-Action-Object relationships
18. Categorize: Useful actions
19. Categorize: Insufficient actions
20. Categorize: Excessive actions
21. Categorize: Harmful actions
22. Research harm elimination examples
23. Identify Technical Contradictions
24. Identify Physical Contradictions
25. Research contradiction resolution examples
26. Prioritize problems to solve
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(
    step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
) -> StepInstruction:
    """Generate instruction for Phase 3 steps"""

    if step_num == 17:
        return StepInstruction(
            task="Map ALL Subject-Action-Object relationships in the system",
            search_queries=[
                f"component interactions functions {problem[:50]}",
                f"how components work together {problem[:50]}",
                "subject action object function analysis",
                "functional modeling system interactions",
            ],
            extract_requirements=[
                "function_list",  # All Subject-Action-Object triplets
                "subjects",  # All subjects (actors)
                "objects",  # All objects (receivers)
                "actions",  # All actions (verbs)
            ],
            validation_criteria="Must identify at least 10 Subject-Action-Object relationships",
            expected_output_format="""
            {
                "functions": [
                    {"subject": "component", "action": "supports", "object": "circuits", "type": "to_determine"},
                    {"subject": "component", "action": "protects", "object": "engine", "type": "to_determine"},
                    {"subject": "aluminum", "action": "adds weight to", "object": "robot", "type": "to_determine"},
                    {"subject": "sheet metal", "action": "allows bending of", "object": "component", "type": "to_determine"},
                    {"subject": "material", "action": "resists", "object": "deformation", "type": "to_determine"}
                ]
            }
            """,
            why_this_matters="Function Analysis reveals the complete system structure and ALL problems (insufficient, excessive, harmful).",
            related_triz_tool="Function Analysis - Subject-Action-Object",
        )

    elif step_num == 18:
        return StepInstruction(
            task="Categorize USEFUL functions (desired and adequate)",
            search_queries=[
                f"desired functions requirements {problem[:50]}",
                f"what should work well {problem[:50]}",
                "useful actions adequate performance",
            ],
            extract_requirements=[
                "useful_functions",  # Functions working well
                "adequacy_rating",  # How adequate (1-10)
                "why_useful",  # Why these are good
            ],
            validation_criteria="Must identify at least 5 useful functions from step 17",
            expected_output_format="""
            {
                "useful": [
                    {
                        "subject": "component",
                        "action": "supports",
                        "object": "circuits",
                        "adequacy": 8,
                        "why": "Provides good structural support for electronics"
                    },
                    {
                        "subject": "component",
                        "action": "protects",
                        "object": "engine",
                        "adequacy": 7,
                        "why": "Adequate protection from minor impacts"
                    }
                ]
            }
            """,
            why_this_matters="Identifying useful functions ensures we preserve what works when improving the system.",
            related_triz_tool="Function Analysis - Useful Actions",
        )

    elif step_num == 19:
        return StepInstruction(
            task="Categorize INSUFFICIENT functions (desired but not enough)",
            search_queries=[
                f"inadequate weak insufficient {problem[:50]}",
                f"needs improvement not enough {problem[:50]}",
                "performance gaps shortfalls deficiencies",
            ],
            extract_requirements=[
                "insufficient_functions",  # Functions that are weak
                "desired_level",  # What level is needed (1-10)
                "current_level",  # What level is now (1-10)
                "gap_size",  # How big is the gap?
            ],
            validation_criteria="Must identify at least 3 insufficient functions with gap analysis",
            expected_output_format="""
            {
                "insufficient": [
                    {
                        "subject": "material",
                        "action": "reduces weight of",
                        "object": "robot",
                        "current_level": 4,
                        "desired_level": 9,
                        "gap": 5,
                        "why": "Aluminum too heavy, need CFRP-like lightness"
                    },
                    {
                        "subject": "component",
                        "action": "allows forming of",
                        "object": "shape",
                        "current_level": 6,
                        "desired_level": 9,
                        "gap": 3,
                        "why": "CFRP difficult to form, need easier formability"
                    }
                ]
            }
            """,
            why_this_matters="Insufficient functions are improvement opportunities. These will be enhanced with Standard Solutions.",
            related_triz_tool="Function Analysis - Insufficient Actions + 76 Standard Solutions",
        )

    elif step_num == 20:
        return StepInstruction(
            task="Categorize EXCESSIVE functions (desired but too much)",
            search_queries=[
                f"excessive too much overkill {problem[:50]}",
                f"overdesigned overengineered {problem[:50]}",
                "waste excess unnecessary redundancy",
            ],
            extract_requirements=[
                "excessive_functions",  # Functions that are too strong
                "optimal_level",  # What level is optimal (1-10)
                "current_level",  # What level is now (1-10)
                "waste_impact",  # What waste does this cause?
            ],
            validation_criteria="Must identify at least 2 excessive functions if any exist",
            expected_output_format="""
            {
                "excessive": [
                    {
                        "subject": "aluminum",
                        "action": "provides strength to",
                        "object": "structure",
                        "optimal_level": 6,
                        "current_level": 9,
                        "excess": 3,
                        "waste": "Over-strength adds unnecessary weight and cost",
                        "opportunity": "Could use thinner material or lighter alloy"
                    }
                ]
            }
            """,
            why_this_matters="Excessive functions waste resources. Trimming or reducing these increases Ideality.",
            related_triz_tool="Function Analysis - Excessive Actions + Trimming",
        )

    elif step_num == 21:
        return StepInstruction(
            task="Categorize HARMFUL functions (undesired outputs)",
            search_queries=[
                f"harmful negative undesired {problem[:50]}",
                f"problems failures defects {problem[:50]}",
                f"side effects drawbacks {problem[:50]}",
                "harmful actions damage waste",
            ],
            extract_requirements=[
                "harmful_functions",  # Harmful actions
                "severity",  # How bad (1-10)
                "impact",  # What damage/harm?
                "source",  # Where found in research?
            ],
            validation_criteria="Must identify at least 4 harmful functions with severity ratings",
            expected_output_format="""
            {
                "harmful": [
                    {
                        "subject": "aluminum",
                        "action": "adds weight to",
                        "object": "robot",
                        "severity": 8,
                        "impact": "Reduces mobility, increases energy consumption, limits runtime",
                        "source": "user_complaints + performance_data"
                    },
                    {
                        "subject": "CFRP",
                        "action": "resists forming of",
                        "object": "component",
                        "severity": 7,
                        "impact": "Cannot be bent/shaped during assembly, requires pre-forming",
                        "source": "manufacturing_handbook"
                    },
                    {
                        "subject": "forming_process",
                        "action": "consumes time for",
                        "object": "manufacturing",
                        "severity": 5,
                        "impact": "Slows production, increases cost",
                        "source": "production_data"
                    }
                ]
            }
            """,
            why_this_matters="Harmful functions are problems to solve with 76 Standard Solutions (eliminate, block, convert to good, correct).",
            related_triz_tool="Function Analysis - Harmful Actions + 76 Standard Solutions",
        )

    elif step_num == 22:
        return StepInstruction(
            task="Research how others eliminate similar harmful functions",
            search_queries=[
                "weight reduction techniques lightweight structures",
                "eliminate harmful actions TRIZ examples",
                "solve formability problems composite materials",
                "harm elimination standard solutions",
            ],
            extract_requirements=[
                "elimination_examples",  # How others eliminated harms
                "applicable_methods",  # Which can we use?
                "standard_solutions_found",  # Standard Solutions identified
            ],
            validation_criteria="Must find at least 5 harm elimination examples from research",
            expected_output_format="""
            {
                "examples": [
                    {
                        "harm": "excessive weight",
                        "elimination_method": "use honeycomb/foam sandwich structure",
                        "principle": "Segmentation + Porous materials",
                        "source": "aerospace_handbook",
                        "applicability": "HIGH"
                    },
                    {
                        "harm": "poor formability",
                        "elimination_method": "thermoforming - heat material before forming",
                        "principle": "Phase transitions + Preliminary action",
                        "source": "plastics_forming_book",
                        "applicability": "HIGH - magnesium formable when heated"
                    },
                    {
                        "harm": "manufacturing time",
                        "elimination_method": "self-forming materials (shape memory)",
                        "principle": "Self-service + Parameter changes",
                        "source": "smart_materials_journal",
                        "applicability": "MEDIUM - emerging technology"
                    }
                ]
            }
            """,
            why_this_matters="Research reveals proven harm elimination methods from other domains and contexts.",
            related_triz_tool="76 Standard Solutions + Cross-Domain Transfer",
        )

    elif step_num == 23:
        return StepInstruction(
            task="Identify TECHNICAL CONTRADICTIONS (improving X worsens Y)",
            search_queries=[
                f"trade-offs compromises {problem[:50]}",
                f"improving one parameter worsens another {problem[:50]}",
                "technical contradictions TRIZ 39 parameters",
                "design trade-offs engineering compromises",
            ],
            extract_requirements=[
                "contradictions_list",  # All technical contradictions
                "improving_parameter",  # What improves
                "worsening_parameter",  # What worsens
                "evidence",  # Research evidence
            ],
            validation_criteria="Must identify at least 2 technical contradictions with clear trade-offs",
            expected_output_format="""
            {
                "technical_contradictions": [
                    {
                        "description": "Using CFRP reduces weight BUT worsens formability",
                        "improving": "Weight of moving object",
                        "improving_number": 1,
                        "worsening": "Ease of manufacture",
                        "worsening_number": 32,
                        "evidence": "CFRP density 1.6 g/cm³ (good) but requires pre-forming/molding (bad)",
                        "source": "composites_handbook"
                    },
                    {
                        "description": "Increasing strength requires thicker material which increases weight",
                        "improving": "Strength",
                        "improving_number": 14,
                        "worsening": "Weight of moving object",
                        "worsening_number": 1,
                        "evidence": "Stronger materials or more thickness = more weight",
                        "source": "mechanics_of_materials"
                    }
                ]
            }
            """,
            why_this_matters="Technical contradictions are resolved with 40 Inventive Principles via Contradiction Matrix.",
            related_triz_tool="Technical Contradictions + 39 Parameters + Contradiction Matrix",
        )

    elif step_num == 24:
        return StepInstruction(
            task="Identify PHYSICAL CONTRADICTIONS (opposite properties in same object)",
            search_queries=[
                f"opposite requirements conflicting needs {problem[:50]}",
                f"must be both A and B simultaneously {problem[:50]}",
                "physical contradictions TRIZ separation",
                "conflicting properties same parameter",
            ],
            extract_requirements=[
                "physical_contradictions",  # Opposite requirements
                "parameter",  # What parameter
                "requirement_1",  # First requirement
                "requirement_2",  # Opposite requirement
                "separation_methods",  # TIME, SPACE, CONDITION, SYSTEM
            ],
            validation_criteria="Must identify at least 1 physical contradiction with separation methods",
            expected_output_format="""
            {
                "physical_contradictions": [
                    {
                        "parameter": "Material State",
                        "requirement_1": "Must be FLEXIBLE/SOFT during forming and assembly",
                        "requirement_2": "Must be RIGID/HARD during operation and use",
                        "description": "Material needs opposite mechanical properties at different times",
                        "separation_methods": [
                            "TIME - flexible when heated during forming, rigid when cooled in use",
                            "CONDITION - flexible under pressure/temperature, rigid at room conditions",
                            "SYSTEM LEVEL - flexible outer layer for forming, rigid inner core"
                        ],
                        "evidence": "Magnesium alloys, thermoplastics, shape memory alloys exhibit this",
                        "source": "materials_phase_transitions_book"
                    },
                    {
                        "parameter": "Material Density",
                        "requirement_1": "Must be HEAVY/DENSE for strength and rigidity",
                        "requirement_2": "Must be LIGHT/LOW-DENSITY for mobility and efficiency",
                        "separation_methods": [
                            "SPACE - dense at stress points, light elsewhere (topology optimization)",
                            "SYSTEM - dense core for strength, light foam for bulk volume"
                        ],
                        "evidence": "Honeycomb structures, sandwich panels, lattice structures",
                        "source": "structural_optimization_handbook"
                    }
                ]
            }
            """,
            why_this_matters="Physical contradictions often reveal THE KEY INSIGHT. Separation principles lead to breakthrough solutions.",
            related_triz_tool="Physical Contradictions + Separation Principles",
        )

    elif step_num == 25:
        return StepInstruction(
            task="Research how others resolve similar contradictions",
            search_queries=[
                "contradiction resolution examples TRIZ",
                "separation in time space condition system",
                "phase transition solutions materials",
                "conflicting requirements solved",
            ],
            extract_requirements=[
                "resolution_examples",  # How others solved
                "principles_used",  # Which principles
                "separation_applied",  # Which separation
                "applicable_to_problem",  # Can we use this?
            ],
            validation_criteria="Must find at least 5 contradiction resolution examples",
            expected_output_format="""
            {
                "examples": [
                    {
                        "contradiction": "flexible vs rigid",
                        "resolution": "Magnesium thermoforming - heat to 200°C for forming, rigid at room temp",
                        "separation": "TIME",
                        "principles": [36, 35],
                        "principle_names": ["Phase transitions", "Parameter changes"],
                        "source": "magnesium_forming_handbook",
                        "applicability": "VERY HIGH - directly solves our problem"
                    },
                    {
                        "contradiction": "heavy vs light",
                        "resolution": "Sandwich panel - CFRP skins (thin, strong) + foam core (thick, light)",
                        "separation": "SPACE + SYSTEM",
                        "principles": [40, 1],
                        "principle_names": ["Composite materials", "Segmentation"],
                        "source": "composite_structures_book",
                        "applicability": "HIGH - proven in aerospace"
                    }
                ]
            }
            """,
            why_this_matters="Researching actual contradiction resolutions provides concrete, proven solution pathways.",
            related_triz_tool="40 Principles + Separation Principles + Case Studies",
        )

    elif step_num == 26:
        return StepInstruction(
            task="Prioritize problems to solve based on Function Analysis",
            search_queries=[
                "problem prioritization impact analysis",
                "which problems solve first criticality",
                "ideality impact harm severity ranking",
            ],
            extract_requirements=[
                "priority_ranking",  # Ordered list of problems
                "ranking_criteria",  # Why this order?
                "solve_first",  # Top priority
                "ideality_impact",  # Impact on Ideality
            ],
            validation_criteria="Must rank all identified problems with clear justification",
            expected_output_format="""
            {
                "priority_ranking": [
                    {
                        "rank": 1,
                        "problem": "Physical contradiction: flexible vs rigid (Step 24)",
                        "type": "Physical Contradiction",
                        "ideality_impact": "HIGH - resolves key trade-off, enables better material choice",
                        "severity": 9,
                        "solvability": "HIGH - separation in TIME proven with magnesium",
                        "why_first": "This is THE ROOT CAUSE. Solving this unlocks the solution."
                    },
                    {
                        "rank": 2,
                        "problem": "Harmful: aluminum adds weight (Step 21)",
                        "type": "Harmful Function",
                        "ideality_impact": "HIGH - weight is biggest harm (severity 8)",
                        "severity": 8,
                        "solvability": "HIGH - magnesium/composites proven lighter",
                        "why_second": "Biggest harm to Ideality score"
                    },
                    {
                        "rank": 3,
                        "problem": "Technical contradiction: weight vs formability (Step 23)",
                        "type": "Technical Contradiction",
                        "ideality_impact": "MEDIUM - subset of physical contradiction",
                        "severity": 7,
                        "solvability": "HIGH - 40 Principles provide solutions",
                        "why_third": "Solving ranks 1-2 will largely solve this"
                    }
                ],
                "solve_order": [
                    "1. Resolve physical contradiction with separation in TIME (magnesium thermoforming)",
                    "2. Eliminate weight harm by material substitution",
                    "3. Apply 40 Principles to remaining technical contradictions"
                ]
            }
            """,
            why_this_matters="Prioritization ensures we solve ROOT CAUSES first, not just symptoms. Maximum Ideality improvement.",
            related_triz_tool="Function Analysis + Ideality + Root Cause Analysis",
        )

    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 3 (valid: 17-26)")
