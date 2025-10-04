"""
PHASE 4: SELECT SOLUTION TOOLS (Steps 27-32)

Match identified problems to appropriate TRIZ solution tools.
Different problem types require different tools.

Steps:
27. Match problems to TRIZ tool categories
28. For contradictions: Map to 39 Parameters
29. For contradictions: Lookup Contradiction Matrix
30. For harms: Identify Standard Solutions
31. For new functions: Search Effects Database
32. For evolution: Research Trends
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(
    step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
) -> StepInstruction:
    """Generate instruction for Phase 4 steps"""

    # Get prioritized problems from step 26
    priorities = accumulated_knowledge.get("step_26", {}).get("priority_ranking", [])

    if step_num == 27:
        return StepInstruction(
            task="Match each identified problem to appropriate TRIZ solution tools",
            search_queries=[
                "TRIZ tool selection problem matching",
                "when to use 40 principles standard solutions",
                "TRIZ tools decision tree problem types",
            ],
            extract_requirements=[
                "tool_mapping",  # Problem → Tool mapping
                "tools_to_use",  # List of tools needed
                "application_order",  # In what sequence?
            ],
            validation_criteria="Must map all priority problems from Step 26 to specific TRIZ tools",
            expected_output_format="""
            {
                "mapping": [
                    {
                        "problem": "Physical contradiction: flexible vs rigid",
                        "problem_type": "Physical Contradiction",
                        "tools": ["Separation Principles", "40 Inventive Principles"],
                        "specific_approach": "Apply separation in TIME/CONDITION"
                    },
                    {
                        "problem": "Harmful: aluminum adds weight",
                        "problem_type": "Harmful Function",
                        "tools": ["76 Standard Solutions (Harm Elimination)", "Materials Database"],
                        "specific_approach": "Eliminate harm by substitution OR convert harm to benefit"
                    },
                    {
                        "problem": "Technical contradiction: weight vs formability",
                        "problem_type": "Technical Contradiction",
                        "tools": ["Contradiction Matrix", "40 Inventive Principles"],
                        "specific_approach": "Lookup in matrix, apply recommended principles"
                    }
                ],
                "tools_needed": [
                    "Separation Principles (for physical contradictions)",
                    "40 Inventive Principles (for all contradictions)",
                    "76 Standard Solutions (for harmful functions)",
                    "Materials Database (for material substitution)",
                    "Contradiction Matrix (for technical contradictions)"
                ]
            }
            """,
            why_this_matters="Using the RIGHT tool for each problem type is critical. TRIZ has specific tools for specific problems.",
            related_triz_tool="TRIZ Tool Selection Logic",
        )

    elif step_num == 28:
        return StepInstruction(
            task="Map technical contradictions to TRIZ 39 Engineering Parameters",
            search_queries=[
                "TRIZ 39 parameters list definitions",
                "map problem to 39 parameters contradiction matrix",
                f"engineering parameters {problem[:50]}",
            ],
            extract_requirements=[
                "mappings",  # Array of parameter mapping objects with contradiction/improving/worsening/confidence/reasoning
            ],
            validation_criteria="Must map all technical contradictions from Step 23 to 39 Parameters",
            expected_output_format="""
            {
                "mappings": [
                    {
                        "contradiction": "Using CFRP reduces weight BUT worsens formability",
                        "improving": {"name": "Weight of moving object", "number": 1},
                        "worsening": {"name": "Ease of manufacture", "number": 32},
                        "confidence": "HIGH",
                        "reasoning": "Weight directly maps to Parameter 1, formability is manufacturing ease"
                    }
                ]
            }
            """,
            why_this_matters="Correct parameter mapping is crucial for getting right principles from Contradiction Matrix.",
            related_triz_tool="39 Engineering Parameters",
        )

    elif step_num == 29:
        return StepInstruction(
            task="Lookup Contradiction Matrix and extract recommended principles",
            search_queries=[
                "TRIZ contradiction matrix lookup",
                "principles for parameter contradiction",
                f"improve parameter {accumulated_knowledge.get('step_28', {}).get('improving_numbers', ['1'])[0] if accumulated_knowledge.get('step_28') else '1'}",
            ],
            extract_requirements=[
                "lookups",  # Array of matrix lookup objects with improving/worsening/principles_found/principle_names/priority_order/reasoning
            ],
            validation_criteria="Must lookup all parameter pairs from Step 28 in Contradiction Matrix",
            expected_output_format="""
            {
                "lookups": [
                    {
                        "improving": 1,
                        "worsening": 32,
                        "principles_found": [1, 27, 35, 40],
                        "principle_names": ["Segmentation", "Cheap short-living objects", "Parameter changes", "Composite materials"],
                        "priority_order": [40, 1, 35, 27],
                        "reasoning": "Principle 40 (Composites) most relevant, then 1 (Segmentation)"
                    }
                ]
            }
            """,
            why_this_matters="Contradiction Matrix provides statistically proven principles that solved similar contradictions in patents.",
            related_triz_tool="Contradiction Matrix",
        )

    elif step_num == 30:
        return StepInstruction(
            task="Identify applicable Standard Solutions for harmful functions",
            search_queries=[
                "TRIZ standard solutions harm elimination",
                "trimming standard solutions TRIZ",
                "eliminate block convert correct harm TRIZ",
            ],
            extract_requirements=[
                "solutions",  # Array of standard solution objects with harm/severity/strategies
            ],
            validation_criteria="Must identify Standard Solutions for all harmful functions from Step 21",
            expected_output_format="""
            {
                "solutions": [
                    {
                        "harm": "aluminum adds weight",
                        "severity": 8,
                        "strategies": [
                            {
                                "strategy": "ELIMINATE",
                                "standard_solution": "Material substitution",
                                "how": "Replace aluminum with lighter material (magnesium, CFRP)",
                                "expected_result": "34-41% weight reduction"
                            },
                            {
                                "strategy": "CONVERT TO GOOD",
                                "standard_solution": "Use harm for benefit",
                                "how": "Use removed aluminum for other functions OR sell as recycled material",
                                "expected_result": "Revenue from waste"
                            }
                        ]
                    }
                ]
            }
            """,
            why_this_matters="Standard Solutions provide systematic approaches to common problem types like harmful functions.",
            related_triz_tool="76 Standard Solutions",
        )

    elif step_num == 31:
        return StepInstruction(
            task="Search Effects Database for new functions or capabilities needed",
            search_queries=[
                "TRIZ effects database scientific effects",
                "how to achieve function physics chemistry",
                f"physical effects {problem[:50]}",
            ],
            extract_requirements=[
                "functions_needed",  # What functions to add?
                "effects_found",  # Scientific effects that deliver function
                "implementation_examples",  # Real-world examples
            ],
            validation_criteria="Must search for effects that deliver insufficient functions from Step 19",
            expected_output_format="""
            {
                "needs": [
                    {
                        "function": "heat material for forming",
                        "x_factor": "System heats material",
                        "effects_found": [
                            {
                                "effect": "Resistive heating",
                                "how": "Pass electric current through material",
                                "example": "Resistance spot welding",
                                "applicability": "MEDIUM - requires conductive material"
                            },
                            {
                                "effect": "Induction heating",
                                "how": "Use electromagnetic field to induce currents",
                                "example": "Induction cookware",
                                "applicability": "HIGH - works with metals like magnesium"
                            }
                        ]
                    }
                ]
            }
            """,
            why_this_matters="Effects Database connects desired functions to proven scientific/engineering methods to achieve them.",
            related_triz_tool="TRIZ Effects Database (X-Factor)",
        )

    elif step_num == 32:
        return StepInstruction(
            task="Research applicable Evolution Trends for system development",
            search_queries=[
                "TRIZ 8 trends technical evolution",
                "system evolution S-curve stages",
                f"future development trends {problem[:50]}",
            ],
            extract_requirements=[
                "current_evolution_stage",  # Where are we on S-curve?
                "applicable_trends",  # Which trends apply?
                "next_generation_features",  # What's next?
                "innovation_opportunities",  # Evolution-based opportunities
            ],
            validation_criteria="Must identify current evolution stage and at least 2 applicable trends",
            expected_output_format="""
            {
                "evolution_analysis": {
                    "s_curve_stage": "Youth to Maturity transition",
                    "evidence": "Aluminum robots mature, composite robots emerging",
                    "trends_applicable": [
                        {
                            "trend": "Increasing Dynamism",
                            "current": "Fixed aluminum structure",
                            "next": "Adaptive/flexible structure",
                            "opportunity": "Shape-memory alloys, morphing structures"
                        },
                        {
                            "trend": "Segmentation + Use of Fields",
                            "current": "Solid sheet aluminum",
                            "next": "Segmented/honeycomb with smart materials",
                            "opportunity": "Sandwich composites with embedded sensors"
                        }
                    ]
                }
            }
            """,
            why_this_matters="Evolution Trends help predict and design next-generation systems, staying ahead of competition.",
            related_triz_tool="8 Trends of Technical Evolution + S-Curve",
        )

    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 4 (valid: 27-32)")
