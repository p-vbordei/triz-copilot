"""
PHASE 2: DEFINE IDEAL OUTCOME (Steps 11-16)

Create "North Star" vision without constraints.
Identify all resources available.
Define what PERFECT looks like.

Steps:
11. Create Ideal Outcome wish list (all desired benefits)
12. Research ideal systems in other domains
13. Identify Resources (Substance, Field, Space, Time)
14. Research resource utilization examples
15. Define Ideal System in 9 Boxes
16. Calculate Ideal Ideality target
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(
    step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
) -> StepInstruction:
    """Generate instruction for Phase 2 steps"""

    if step_num == 11:
        return StepInstruction(
            task="Create Ideal Outcome wish list - ALL desired benefits without constraints",
            search_queries=[
                f"ideal perfect solution {problem[:50]}",
                f"utopian best case scenario {problem[:50]}",
                "user dream requirements wishlist",
                "impossible features desired capabilities",
            ],
            extract_requirements=[
                "prime_benefit",  # THE main desired outcome
                "ultimate_goal",  # Long-term vision
                "wish_list",  # All desired benefits
                "constraints_to_ignore",  # What we're ignoring for now
            ],
            validation_criteria="Must list at least 8 desired benefits without considering feasibility",
            expected_output_format="""
            {
                "prime_benefit": "Component is perfectly lightweight and perfectly formable",
                "ultimate_goal": "Zero-weight structural component that shapes itself",
                "wish_list": [
                    "Weighs nothing",
                    "Infinite strength",
                    "Forms itself to any shape",
                    "Costs nothing",
                    "Never fails",
                    "Repairs itself",
                    "Environmentally perfect"
                ],
                "constraints_ignoring": ["physics laws", "budget", "current technology"]
            }
            """,
            why_this_matters="Ideal Outcome breaks psychological inertia. Even 'impossible' wishes guide toward breakthrough solutions.",
            related_triz_tool="Ideal Outcome (IFR - Ideal Final Result)",
        )

    elif step_num == 12:
        return StepInstruction(
            task="Research how other domains achieve similar ideal outcomes",
            search_queries=[
                "cross-domain solutions lightweight structures",
                "nature biomimicry lightweight strong materials",
                "aerospace lightweight formable materials",
                "other industries similar problems solved",
            ],
            extract_requirements=[
                "cross_domain_examples",  # Examples from other fields
                "nature_solutions",  # Biomimicry insights
                "analogous_problems",  # Similar problems elsewhere
                "transfer_potential",  # Can we adapt these?
            ],
            validation_criteria="Must find at least 3 cross-domain examples with specific details",
            expected_output_format="""
            {
                "cross_domain": [
                    {
                        "domain": "nature - bird bones",
                        "solution": "hollow bone structure - light + strong",
                        "principle": "segmentation + porous materials",
                        "transfer": "could use honeycomb/foam core sheet"
                    },
                    {
                        "domain": "aerospace - aircraft panels",
                        "solution": "sandwich composites - CFRP skins + foam core",
                        "principle": "composite materials",
                        "transfer": "directly applicable to robot component"
                    }
                ]
            }
            """,
            why_this_matters="Solutions already exist in other domains. Cross-domain transfer is powerful TRIZ strategy.",
            related_triz_tool="Cross-Domain Solution Transfer",
        )

    elif step_num == 13:
        return StepInstruction(
            task="Identify ALL available Resources (Substance, Field, Space, Time, Information)",
            search_queries=[
                f"available resources materials {problem[:50]}",
                f"existing components capabilities {problem[:50]}",
                f"energy forces fields available {problem[:50]}",
                "waste byproducts reusable resources",
            ],
            extract_requirements=[
                "substance_resources",  # Materials, components
                "field_resources",  # Energy, forces, fields
                "space_resources",  # Available volume, areas
                "time_resources",  # Available time, timing opportunities
                "information_resources",  # Data, knowledge, signals
            ],
            validation_criteria="Must identify at least 10 resources across all 5 types",
            expected_output_format="""
            {
                "substance": [
                    {"name": "aluminum available", "location": "system", "potential": "current material"},
                    {"name": "CFRP mentioned", "location": "super-system", "potential": "target material"},
                    {"name": "waste heat from motors", "location": "sub-system", "potential": "forming energy"}
                ],
                "field": [
                    {"name": "motor vibration", "location": "system", "potential": "energy source"},
                    {"name": "gravity", "location": "super-system", "potential": "free force"}
                ],
                "space": [
                    {"name": "20cm x 4cm area", "location": "system", "potential": "design space"}
                ],
                "time": [
                    {"name": "assembly time", "location": "manufacturing", "potential": "forming window"},
                    {"name": "operation downtime", "location": "usage", "potential": "self-repair time"}
                ],
                "information": [
                    {"name": "user patterns", "location": "super-system", "potential": "predictive optimization"}
                ]
            }
            """,
            why_this_matters="Resources thinking = getting benefits WITHOUT adding new things. Key to increasing Ideality.",
            related_triz_tool="Resources Thinking",
        )

    elif step_num == 14:
        return StepInstruction(
            task="Research how others cleverly use similar resources",
            search_queries=[
                "waste heat utilization manufacturing",
                "vibration energy harvesting applications",
                "gravity assist mechanisms designs",
                "clever resource usage examples TRIZ",
            ],
            extract_requirements=[
                "resource_usage_examples",  # Clever uses found
                "applicable_to_problem",  # Which can we use?
                "inspiration_sources",  # Where found?
            ],
            validation_criteria="Must find at least 4 resource utilization examples from research",
            expected_output_format="""
            {
                "examples": [
                    {
                        "resource": "waste heat",
                        "use": "thermoforming plastics during manufacturing",
                        "source": "manufacturing_handbook",
                        "applicability": "HIGH - could heat-form magnesium with motor waste heat"
                    },
                    {
                        "resource": "gravity",
                        "use": "gravity forming of sheet metal",
                        "source": "metalworking_book",
                        "applicability": "MEDIUM - could assist forming process"
                    }
                ]
            }
            """,
            why_this_matters="Learning how others use resources provides ready-made solutions requiring no new inputs.",
            related_triz_tool="Resources + 40 Principles",
        )

    elif step_num == 15:
        return StepInstruction(
            task="Define IDEAL SYSTEM in 9 Boxes - how would perfection look?",
            search_queries=[
                "ideal system characteristics perfect solution",
                f"future ideal state {problem[:50]}",
                "breakthrough innovations revolutionary designs",
            ],
            extract_requirements=[
                "ideal_sub_system",  # Perfect components
                "ideal_system",  # Perfect system
                "ideal_super_system",  # Perfect context
                "path_to_ideal",  # How to get there?
            ],
            validation_criteria="Must define ideal state for all 9 boxes",
            expected_output_format="""
            {
                "ideal_9boxes": {
                    "sub_system": "Zero-weight self-forming smart material",
                    "system": "Adaptive robot with shape-changing structure",
                    "super_system": "Seamless human-robot interaction ecosystem"
                },
                "gap_analysis": {
                    "current_to_ideal_gap": "Current: aluminum 2.7g/cm³ → Ideal: <1.0g/cm³",
                    "path": "Magnesium (1.78) → Composites (1.5) → Future materials"
                }
            }
            """,
            why_this_matters="Ideal System in 9 Boxes shows the North Star across all system levels and time.",
            related_triz_tool="9 Boxes + Ideal Outcome",
        )

    elif step_num == 16:
        return StepInstruction(
            task="Calculate IDEAL Ideality target score",
            search_queries=[
                "ideality maximization TRIZ methodology",
                "perfect system characteristics infinite benefits",
                "zero cost zero harm ideal calculation",
            ],
            extract_requirements=[
                "ideal_benefits_total",  # Maximum possible
                "ideal_costs",  # Minimum (ideally 0)
                "ideal_harms",  # Minimum (ideally 0)
                "ideal_ideality_score",  # Target number
                "gap_from_current",  # How far are we?
            ],
            validation_criteria="Must calculate ideal Ideality and compare to current from Step 9",
            expected_output_format="""
            {
                "ideal_calculation": {
                    "ideal_benefits": 100.0,
                    "ideal_costs": 5.0,
                    "ideal_harms": 0.0,
                    "ideal_ideality": 20.0,
                    "category": "UTOPIAN"
                },
                "current_vs_ideal": {
                    "current_ideality": 0.904,
                    "ideal_ideality": 20.0,
                    "gap": "22x improvement needed",
                    "improvement_potential": "MASSIVE"
                },
                "priorities": [
                    "Reduce weight harm (biggest drag)",
                    "Increase formability benefit (biggest upside)",
                    "Eliminate manufacturing costs where possible"
                ]
            }
            """,
            why_this_matters="Ideal Ideality target quantifies how much improvement is possible and guides priorities.",
            related_triz_tool="Ideality Equation + Gap Analysis",
        )

    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 2 (valid: 11-16)")
