"""
PHASE 1: UNDERSTAND & SCOPE PROBLEM (Steps 1-10)

This is THE MOST CRITICAL PHASE - it sets up the entire TRIZ analysis.
Without proper scoping with 9 Boxes and Ideality Audit, the rest will fail.

Steps:
1. Create 9 Boxes context map (Past-Present-Future × Sub-System-System-Super)
2. Research Sub-System components
3. Research Super-System environment
4. Analyze Past evolution
5. Analyze Future trends
6. Calculate current Ideality (Benefits/(Costs+Harms))
7. List all current Benefits
8. List all current Costs
9. List all current Harms
10. Identify root causes from 9 Boxes
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(
    step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
) -> StepInstruction:
    """Generate instruction for Phase 1 steps"""

    if step_num == 1:
        return StepInstruction(
            task="Create 9 Boxes context map for complete system understanding",
            search_queries=[
                f"components parts inside {problem[:50]}",
                f"environment context where {problem[:50]} operates",
                f"historical evolution development {problem[:50]}",
                f"future trends predictions {problem[:50]}",
            ],
            extract_requirements=[
                "sub_system_components",  # What's inside the system?
                "system_description",  # The system itself
                "super_system_context",  # Environment/users/market
                "past_evolution",  # How did it evolve?
                "future_predictions",  # Where is it going?
            ],
            validation_criteria="Must identify at least 3 items for sub-system, system, and super-system across time",
            expected_output_format="""
            {
                "sub_system_past": ["component1", "component2"],
                "sub_system_present": ["current_component1", "current_component2"],
                "sub_system_future": ["predicted_component1"],
                "system_past": ["previous_version"],
                "system_present": ["current_system"],
                "system_future": ["next_generation"],
                "super_system_past": ["old_market", "old_users"],
                "super_system_present": ["current_market", "current_users"],
                "super_system_future": ["predicted_market", "predicted_users"]
            }
            """,
            why_this_matters="9 Boxes provides complete context before diving into details. It reveals trends, root causes, and future opportunities that narrow analysis would miss.",
            related_triz_tool="9 Boxes (Time & Scale Thinking)",
        )

    elif step_num == 2:
        return StepInstruction(
            task="Deep research on Sub-System components (what's INSIDE the system)",
            search_queries=[
                f"internal components parts {problem[:50]}",
                f"subsystem elements materials {problem[:50]}",
                f"component materials properties {problem[:50]}",
                "component interactions interfaces connections",
            ],
            extract_requirements=[
                "component_list",  # All identified components
                "component_materials",  # What they're made of
                "component_functions",  # What each does
                "component_interactions",  # How they connect
            ],
            validation_criteria="Must identify at least 5 specific sub-system components with materials",
            expected_output_format="""
            {
                "components": [
                    {"name": "component1", "material": "aluminum", "function": "structural support"},
                    {"name": "component2", "material": "copper", "function": "electrical connection"}
                ],
                "interactions": ["component1 connects to component2 via bolts"]
            }
            """,
            why_this_matters="Understanding sub-system reveals where problems truly originate and what resources are available.",
            related_triz_tool="9 Boxes - Sub-System Level",
        )

    elif step_num == 3:
        return StepInstruction(
            task="Deep research on Super-System (environment, users, market context)",
            search_queries=[
                f"user requirements needs {problem[:50]}",
                f"market trends environment {problem[:50]}",
                f"operating conditions constraints {problem[:50]}",
                f"competitors alternatives {problem[:50]}",
            ],
            extract_requirements=[
                "users",  # Who uses it?
                "user_needs",  # What do they need?
                "operating_environment",  # Where does it operate?
                "market_context",  # Market/industry context
                "competitors_alternatives",  # What else exists?
            ],
            validation_criteria="Must identify users, environment, and at least 2 competitors/alternatives",
            expected_output_format="""
            {
                "users": ["household owners", "elderly people"],
                "user_needs": ["follow without effort", "capture moments"],
                "operating_environment": "indoor household, room temperature, furniture obstacles",
                "market_context": "home robotics market growing 15% annually",
                "competitors": ["static tripod", "selfie stick", "professional videographer"]
            }
            """,
            why_this_matters="Super-system reveals true requirements and constraints. Solutions must fit the broader context.",
            related_triz_tool="9 Boxes - Super-System Level",
        )

    elif step_num == 4:
        return StepInstruction(
            task="Analyze PAST evolution (how did we get here?)",
            search_queries=[
                f"history evolution development {problem[:50]}",
                f"previous generation older version {problem[:50]}",
                f"historical problems failures {problem[:50]}",
                "lessons learned from past designs",
            ],
            extract_requirements=[
                "past_systems",  # What came before?
                "past_problems",  # What failed?
                "evolution_path",  # How did it evolve?
                "lessons_learned",  # What did we learn?
            ],
            validation_criteria="Must identify at least 2 previous generations and their key problems",
            expected_output_format="""
            {
                "past_systems": [
                    {"era": "1990s", "system": "manual tripod", "problems": ["static", "no movement"]},
                    {"era": "2000s", "system": "motorized pan-tilt", "problems": ["heavy", "complex"]}
                ],
                "evolution_path": "static → motorized → autonomous",
                "lessons_learned": ["weight reduction critical", "simplicity important"]
            }
            """,
            why_this_matters="Understanding past evolution reveals patterns and helps avoid repeating mistakes.",
            related_triz_tool="9 Boxes - Past Timeline + S-Curve Evolution",
        )

    elif step_num == 5:
        return StepInstruction(
            task="Analyze FUTURE trends (where is this going?)",
            search_queries=[
                f"future trends predictions {problem[:50]}",
                f"next generation emerging technology {problem[:50]}",
                f"innovation roadmap future development {problem[:50]}",
                "future user expectations requirements",
            ],
            extract_requirements=[
                "future_trends",  # What trends exist?
                "emerging_technologies",  # New tech coming?
                "future_user_needs",  # Changing requirements?
                "predicted_problems",  # Future challenges?
            ],
            validation_criteria="Must identify at least 3 future trends with evidence from research",
            expected_output_format="""
            {
                "future_trends": [
                    {"trend": "AI integration", "evidence": "85% of robots will have AI by 2030", "source": "robotics_journal"},
                    {"trend": "lightweight materials", "evidence": "carbon fiber demand growing", "source": "materials_book"}
                ],
                "emerging_technologies": ["AI vision", "LiDAR", "shape-memory alloys"],
                "future_user_needs": ["voice control", "gesture recognition"],
                "predicted_problems": ["battery life", "privacy concerns"]
            }
            """,
            why_this_matters="Future analysis helps design solutions that will remain relevant and anticipate next problems.",
            related_triz_tool="9 Boxes - Future Timeline + 8 Trends of Evolution",
        )

    elif step_num == 6:
        return StepInstruction(
            task="Identify all current BENEFITS (desired outcomes) for Ideality calculation",
            search_queries=[
                f"benefits advantages desired outcomes {problem[:50]}",
                f"what users want value proposition {problem[:50]}",
                f"performance metrics success criteria {problem[:50]}",
                "functional requirements specifications",
            ],
            extract_requirements=[
                "benefits_list",  # All benefits
                "benefit_importance",  # Rank 1-10
                "current_achievement",  # How well achieved now (0-10)
            ],
            validation_criteria="Must identify at least 5 distinct benefits with importance rankings",
            expected_output_format="""
            {
                "benefits": [
                    {"description": "follows user smoothly", "importance": 10, "current_achievement": 6, "source": "user_requirements"},
                    {"description": "lightweight portable", "importance": 9, "current_achievement": 4, "source": "market_research"},
                    {"description": "captures stable video", "importance": 8, "current_achievement": 7, "source": "product_specs"}
                ]
            }
            """,
            why_this_matters="Benefits are the numerator in Ideality equation. We maximize these to increase Ideality.",
            related_triz_tool="Ideality Equation - Benefits",
        )

    elif step_num == 7:
        return StepInstruction(
            task="Identify all current COSTS (inputs required) for Ideality calculation",
            search_queries=[
                f"costs price materials resources {problem[:50]}",
                f"manufacturing costs production expenses {problem[:50]}",
                f"time effort energy required {problem[:50]}",
                "resource consumption inputs needed",
            ],
            extract_requirements=[
                "costs_list",  # All costs
                "cost_magnitude",  # Rank 1-10
                "cost_type",  # money, time, materials, effort, energy
            ],
            validation_criteria="Must identify at least 5 distinct costs across different types",
            expected_output_format="""
            {
                "costs": [
                    {"description": "aluminum sheet material", "magnitude": 6, "type": "money", "source": "materials_catalog"},
                    {"description": "forming/bending process", "magnitude": 5, "type": "time", "source": "manufacturing_book"},
                    {"description": "assembly labor", "magnitude": 7, "type": "effort", "source": "production_data"}
                ]
            }
            """,
            why_this_matters="Costs are in denominator of Ideality. We minimize these to increase Ideality.",
            related_triz_tool="Ideality Equation - Costs",
        )

    elif step_num == 8:
        return StepInstruction(
            task="Identify all current HARMS (undesired outputs) for Ideality calculation",
            search_queries=[
                f"problems issues drawbacks {problem[:50]}",
                f"side effects negative impacts {problem[:50]}",
                f"waste byproducts inefficiency {problem[:50]}",
                "failures defects complaints",
            ],
            extract_requirements=[
                "harms_list",  # All harms
                "harm_severity",  # Rank 1-10
                "harm_type",  # safety, environmental, waste, side-effects
            ],
            validation_criteria="Must identify at least 3 distinct harms with severity rankings",
            expected_output_format="""
            {
                "harms": [
                    {"description": "excessive weight reduces mobility", "severity": 8, "type": "performance", "source": "user_complaints"},
                    {"description": "aluminum waste from cutting", "severity": 4, "type": "environmental", "source": "manufacturing_data"},
                    {"description": "difficult to form requires heat", "severity": 6, "type": "manufacturing", "source": "process_manual"}
                ]
            }
            """,
            why_this_matters="Harms are in denominator of Ideality. We minimize/eliminate these to increase Ideality.",
            related_triz_tool="Ideality Equation - Harms",
        )

    elif step_num == 9:
        return StepInstruction(
            task="Calculate current Ideality score and analyze system health",
            search_queries=[
                "ideality calculation TRIZ methodology",
                f"system performance evaluation {problem[:50]}",
                "benchmarking comparison analysis",
            ],
            extract_requirements=[
                "ideality_calculation",  # Sum(Benefits)/(Sum(Costs)+Sum(Harms))
                "ideality_score",  # Numerical value
                "ideality_category",  # EXCELLENT/GOOD/ACCEPTABLE/POOR
                "key_insights",  # What does this reveal?
            ],
            validation_criteria="Must calculate Ideality score using data from steps 6-8",
            expected_output_format="""
            {
                "calculation": {
                    "total_benefits": 45.2,
                    "total_costs": 32.0,
                    "total_harms": 18.0,
                    "ideality_score": 0.904,
                    "category": "ACCEPTABLE"
                },
                "insights": [
                    "Weight harm (severity 8) is major drag on Ideality",
                    "Following function (importance 10, achievement 6) has improvement potential",
                    "Current system is acceptable but far from ideal"
                ]
            }
            """,
            why_this_matters="Ideality score reveals system health and guides improvement priorities.",
            related_triz_tool="Ideality Audit",
        )

    elif step_num == 10:
        return StepInstruction(
            task="Identify root causes and patterns from 9 Boxes analysis",
            search_queries=[
                "root cause analysis problem identification",
                f"underlying causes patterns {problem[:50]}",
                "system thinking causal relationships",
            ],
            extract_requirements=[
                "root_causes",  # Fundamental causes
                "patterns_observed",  # Trends/patterns from 9 Boxes
                "key_contradictions",  # Emerging contradictions
                "priority_problems",  # What to solve first?
            ],
            validation_criteria="Must identify at least 2 root causes with evidence from 9 Boxes",
            expected_output_format="""
            {
                "root_causes": [
                    {
                        "cause": "Material choice drives weight-formability trade-off",
                        "evidence": "9 Boxes shows: Past (heavy steel) → Present (lighter aluminum) → Future (need lighter still)",
                        "impacts": ["mobility", "energy consumption", "manufacturing"]
                    }
                ],
                "patterns": [
                    "Evolution trend: increasing lightness + increasing formability difficulty",
                    "Super-system pressure: users demand lighter, market offers CFRP alternatives"
                ],
                "key_contradictions": [
                    "Need lightweight (CFRP) BUT need formability (aluminum)"
                ],
                "priorities": ["Solve weight-formability contradiction", "Find lighter formable material"]
            }
            """,
            why_this_matters="Root cause analysis from 9 Boxes reveals the TRUE problems to solve, not just symptoms.",
            related_triz_tool="9 Boxes Analysis + Root Cause Thinking",
        )

    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 1 (valid: 1-10)")
