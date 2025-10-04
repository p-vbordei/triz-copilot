"""
PHASE 5: GENERATE SOLUTIONS (Steps 33-50)

Apply ALL selected TRIZ tools to generate comprehensive solution set.
This is the LONGEST phase with 18 steps of deep research.

Steps:
33. Deep research Principle #1 from matrix (full description)
34. Find real-world examples of Principle #1
35. Extract sub-principles and variations of Principle #1
36. Apply Principle #1 to your specific problem
37. Deep research Principle #2 from matrix (full description)
38. Find real-world examples of Principle #2
39. Extract sub-principles and variations of Principle #2
40. Apply Principle #2 to your specific problem
41. Research Principle #3 (if applicable)
42. Apply Standard Solution: Eliminate harm
43. Apply Standard Solution: Block harm (if elimination impossible)
44. Apply Standard Solution: Convert harm to benefit
45. Apply Standard Solution: Enhance insufficient functions
46. Research effects from Effects Database for new functions
47. DEEP materials research (if materials problem detected)
48. Extract material properties: densities, strengths, formability
49. Create material comparison tables
50. Generate complete solution concepts combining all tools
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(
    step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
) -> StepInstruction:
    """Generate instruction for Phase 5 steps"""

    # Get recommended principles from step 29
    principles = accumulated_knowledge.get("step_29", {}).get(
        "recommended_principles", [1, 15, 35]
    )

    # Get harmful functions from step 21
    harms = accumulated_knowledge.get("step_21", {}).get("harmful_functions", [])

    # Get insufficient functions from step 19
    insufficient = accumulated_knowledge.get("step_19", {}).get(
        "insufficient_functions", []
    )

    # Get effects needed from step 31
    effects_needed = accumulated_knowledge.get("step_31", {}).get(
        "functions_needed", []
    )

    if step_num == 33:
        # Get first principle number from matrix results
        principle_num = principles[0] if principles else 1

        return StepInstruction(
            task=f"Deep research TRIZ Principle #{principle_num} - read FULL description from knowledge base",
            search_queries=[
                f"TRIZ principle {principle_num} full description complete text",
                f"principle {principle_num} definition explanation approach",
                f"how to apply principle {principle_num} methodology",
                f"principle {principle_num} sub-principles variations",
                f"when to use principle {principle_num} situations",
            ],
            extract_requirements=[
                "principle_number",
                "principle_name",
                "full_description",  # Complete description, not summary
                "general_approach",  # How it works conceptually
                "when_to_use",  # Appropriate situations
            ],
            validation_criteria=f"Must extract COMPLETE description of Principle #{principle_num} with at least 200 words",
            expected_output_format=f"""
            {{
                "principle_number": {principle_num},
                "principle_name": "Example: Segmentation",
                "full_description": "COMPLETE multi-paragraph description from TRIZ books: Divide an object into independent parts, make an object easy to disassemble, increase the degree of fragmentation or segmentation. This principle suggests breaking down a system into smaller parts that can operate independently, be easily assembled and disassembled, or divided into increasingly smaller segments. The principle is based on the observation that systems often benefit from being divisible rather than monolithic...",
                "general_approach": "This principle works by decomposing systems into modular components that can be optimized independently, assembled in different configurations, or replaced individually without affecting the whole system.",
                "when_to_use": "Use this when you need flexibility, easier maintenance, customization, or when different parts require different properties. Particularly effective for overcoming physical contradictions by allowing different parts to have different properties.",
                "source": "TRIZ_40_principles_complete"
            }}
            """,
            why_this_matters=f"Understanding the FULL principle #{principle_num} is critical before applying it. Shallow understanding leads to poor solutions. The Contradiction Matrix recommended this principle based on patterns from thousands of patents - we must understand WHY it works.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num}",
        )

    elif step_num == 34:
        principle_num = accumulated_knowledge.get("step_33", {}).get(
            "principle_number", principles[0] if principles else 1
        )

        return StepInstruction(
            task=f"Find real-world examples of Principle #{principle_num} in action across multiple industries",
            search_queries=[
                f"principle {principle_num} examples case studies real applications",
                f"principle {principle_num} applications industry success stories",
                f"companies used principle {principle_num} innovation",
                f"principle {principle_num} patents implementations products",
            ],
            extract_requirements=[
                "examples",  # Array of example objects with example/domain/application/results/source/applicability
            ],
            validation_criteria=f"Must find at least 5 real-world examples of Principle #{principle_num} from diverse industries",
            expected_output_format="""
            {
                "examples": [
                    {
                        "example": "LEGO modular toy system using segmentation",
                        "domain": "consumer products/toys",
                        "application": "Divided toy system into standardized blocks that connect via universal interface, allowing infinite configurations",
                        "results": "Market dominance, billions in revenue, endless customization",
                        "source": "TRIZ_case_studies",
                        "applicability": "HIGH - we can segment our system into modular components with standard interfaces"
                    },
                    {
                        "example": "Automotive modular platform architecture (VW MQB)",
                        "domain": "automotive",
                        "application": "Segmented vehicle into modules (chassis, powertrain, body) shared across models",
                        "results": "40% cost reduction, faster development, easier customization",
                        "source": "engineering_journal",
                        "applicability": "MEDIUM - modularity principle applies but scale different"
                    },
                    {
                        "example": "Shipping container standardization",
                        "domain": "logistics",
                        "application": "Segmented cargo into standard 20/40ft containers with universal handling",
                        "results": "Revolutionized global trade, 90% cost reduction",
                        "source": "logistics_history",
                        "applicability": "HIGH - standardization + segmentation creates flexibility"
                    },
                    {
                        "example": "Microservices software architecture",
                        "domain": "software",
                        "application": "Divided monolithic software into independent services",
                        "results": "Easier scaling, faster updates, better reliability",
                        "source": "software_engineering",
                        "applicability": "MEDIUM - same principle different domain"
                    },
                    {
                        "example": "Snap-fit plastic assembly in consumer electronics",
                        "domain": "manufacturing",
                        "application": "Segmented product into snap-together parts, no screws/glues",
                        "results": "Assembly time reduced 80%, disassembly for recycling easy",
                        "source": "manufacturing_handbook",
                        "applicability": "HIGH - can apply snap-fit segmentation to our components"
                    }
                ]
            }
            """,
            why_this_matters=f"Real examples show HOW to apply Principle #{principle_num} in practice, not just theory. Seeing it work across industries reveals universal patterns we can adapt to our specific problem.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num} Examples",
        )

    elif step_num == 35:
        principle_num = accumulated_knowledge.get("step_33", {}).get(
            "principle_number", principles[0] if principles else 1
        )

        return StepInstruction(
            task=f"Extract sub-principles and variations of Principle #{principle_num}",
            search_queries=[
                f"principle {principle_num} sub-principles variations types",
                f"principle {principle_num} different approaches methods",
                f"principle {principle_num} detailed breakdown categories",
                f"how many ways to apply principle {principle_num}",
            ],
            extract_requirements=[
                "sub_principles",  # Array of sub-principle objects with variation/description/example/when_to_use
                "selection_criteria",  # String describing how to choose variation
            ],
            validation_criteria=f"Must identify at least 3 sub-principles or variations of Principle #{principle_num}",
            expected_output_format="""
            {
                "sub_principles": [
                    {
                        "variation": "Divide object into independent parts",
                        "description": "Decompose system into components that operate autonomously",
                        "example": "Modular furniture that can be rearranged",
                        "when_to_use": "When flexibility and reconfiguration needed"
                    },
                    {
                        "variation": "Make object easy to disassemble",
                        "description": "Design for assembly/disassembly with minimal tools",
                        "example": "Snap-fit connections, tool-free assembly",
                        "when_to_use": "When maintenance, repair, or recycling important"
                    },
                    {
                        "variation": "Increase degree of fragmentation",
                        "description": "Break into increasingly smaller segments",
                        "example": "Powder instead of solid, nanoparticles instead of bulk",
                        "when_to_use": "When surface area, mixing, or reactivity critical"
                    }
                ],
                "selection_criteria": "Choose variation based on: (1) primary benefit needed, (2) manufacturing constraints, (3) lifecycle requirements"
            }
            """,
            why_this_matters=f"Principle #{principle_num} has multiple interpretations. Understanding variations helps select the BEST approach for our specific situation rather than generic application.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num} Variations",
        )

    elif step_num == 36:
        principle_num = accumulated_knowledge.get("step_33", {}).get(
            "principle_number", principles[0] if principles else 1
        )
        principle_name = accumulated_knowledge.get("step_33", {}).get(
            "principle_name", f"Principle {principle_num}"
        )

        return StepInstruction(
            task=f"Apply Principle #{principle_num} ({principle_name}) to YOUR specific problem - generate concrete solution concepts",
            search_queries=[
                f"apply principle {principle_num} to {problem[:50]}",
                f"how to use {principle_name} for {problem[:50]}",
                f"principle {principle_num} solution examples similar problems",
                f"{principle_name} implementation engineering design",
            ],
            extract_requirements=[
                "solutions",  # Array of solution concept objects with concept/principle_application/how_it_works/expected_benefits/implementation/challenges/feasibility
            ],
            validation_criteria=f"Must generate at least 3 concrete solution concepts applying Principle #{principle_num} to the problem",
            expected_output_format="""
            {
                "solutions": [
                    {
                        "concept": "Modular segmented structure with snap-fit assembly",
                        "principle_application": "Apply segmentation principle by dividing structure into 5-7 modules connected via standardized snap-fit interfaces",
                        "how_it_works": "Each module optimized for specific function (base, joint, arm, etc.), assembled tool-free, easy to replace/upgrade individual modules",
                        "expected_benefits": ["40% weight reduction via optimized modules", "Easy repair - replace module not whole system", "Customization - swap modules for different needs"],
                        "implementation": "Design snap-fit connectors with 3-point locking, ensure module interfaces standardized, prototype individual modules separately",
                        "challenges": ["Interface strength critical", "Tolerance stackup across modules", "Need design for disassembly guidelines"],
                        "feasibility": "HIGH - snap-fit proven in consumer electronics, modules enable weight optimization"
                    },
                    {
                        "concept": "Honeycomb segmentation of sheet material",
                        "principle_application": "Apply fragmentation variation - segment solid sheet into honeycomb/lattice structure",
                        "how_it_works": "Replace solid aluminum with aluminum honeycomb core (hexagonal cells), maintain strength with 50% less material",
                        "expected_benefits": ["50% weight reduction", "Maintains bending stiffness", "Better energy absorption"],
                        "implementation": "Use honeycomb core with thin face sheets, adhesive bonding or brazing assembly",
                        "challenges": ["Forming honeycomb curves difficult", "More complex manufacturing", "Higher piece-part cost"],
                        "feasibility": "MEDIUM - aerospace proven but cost/manufacturing complexity higher"
                    },
                    {
                        "concept": "Segmented multi-material approach",
                        "principle_application": "Segment system by material - use different materials for different segments based on local requirements",
                        "how_it_works": "High-stress areas: steel/titanium; low-stress areas: polymer/CFRP; assembly via mechanical fasteners",
                        "expected_benefits": ["Optimized weight-strength-cost", "Each segment uses ideal material", "30-40% weight reduction possible"],
                        "implementation": "FEA to identify stress zones, select materials per zone, design multi-material joints",
                        "challenges": ["Thermal expansion mismatch", "Joining dissimilar materials", "More complex supply chain"],
                        "feasibility": "HIGH - automotive industry proven approach (multi-material body structures)"
                    }
                ]
            }
            """,
            why_this_matters=f"This is where TRIZ guidance becomes concrete solutions. We transform abstract Principle #{principle_num} into actionable engineering concepts for our specific problem.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num} Application",
        )

    elif step_num == 37:
        # Get second principle
        principle_num = principles[1] if len(principles) > 1 else 15

        return StepInstruction(
            task=f"Deep research TRIZ Principle #{principle_num} - read FULL description from knowledge base",
            search_queries=[
                f"TRIZ principle {principle_num} full description complete text",
                f"principle {principle_num} definition explanation approach",
                f"how to apply principle {principle_num} methodology",
                f"principle {principle_num} sub-principles variations",
                f"when to use principle {principle_num} situations",
            ],
            extract_requirements=[
                "principle_number",
                "principle_name",
                "full_description",
                "general_approach",
                "when_to_use",
            ],
            validation_criteria=f"Must extract COMPLETE description of Principle #{principle_num} with at least 200 words",
            expected_output_format=f"""
            {{
                "principle_number": {principle_num},
                "principle_name": "Example: Dynamism",
                "full_description": "COMPLETE multi-paragraph description from TRIZ books...",
                "general_approach": "This principle works by...",
                "when_to_use": "Use this when you need...",
                "source": "TRIZ_40_principles_complete"
            }}
            """,
            why_this_matters=f"Principle #{principle_num} was also recommended by Contradiction Matrix. Multiple principles often work together to resolve complex contradictions.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num}",
        )

    elif step_num == 38:
        principle_num = accumulated_knowledge.get("step_37", {}).get(
            "principle_number", principles[1] if len(principles) > 1 else 15
        )

        return StepInstruction(
            task=f"Find real-world examples of Principle #{principle_num} in action across multiple industries",
            search_queries=[
                f"principle {principle_num} examples case studies real applications",
                f"principle {principle_num} applications industry success stories",
                f"companies used principle {principle_num} innovation",
                f"principle {principle_num} patents implementations products",
            ],
            extract_requirements=[
                "examples",  # Array of example objects with example/domain/application/results/source/applicability
            ],
            validation_criteria=f"Must find at least 5 real-world examples of Principle #{principle_num} from diverse industries",
            expected_output_format="""
            {
                "examples": [
                    {
                        "example": "Example description",
                        "domain": "industry/field",
                        "application": "How they applied the principle",
                        "results": "What they achieved",
                        "source": "book_name or journal",
                        "applicability": "HIGH/MEDIUM/LOW - reasoning why"
                    },
                    ... (at least 5 examples)
                ]
            }
            """,
            why_this_matters=f"Real examples show HOW to apply Principle #{principle_num} in practice across different domains.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num} Examples",
        )

    elif step_num == 39:
        principle_num = accumulated_knowledge.get("step_37", {}).get(
            "principle_number", principles[1] if len(principles) > 1 else 15
        )

        return StepInstruction(
            task=f"Extract sub-principles and variations of Principle #{principle_num}",
            search_queries=[
                f"principle {principle_num} sub-principles variations types",
                f"principle {principle_num} different approaches methods",
                f"principle {principle_num} detailed breakdown categories",
                f"how many ways to apply principle {principle_num}",
            ],
            extract_requirements=[
                "sub_principles",  # Array of sub-principle objects with variation/description/example/when_to_use
                "selection_criteria",  # String describing how to choose variation
            ],
            validation_criteria=f"Must identify at least 3 sub-principles or variations of Principle #{principle_num}",
            expected_output_format="""
            {
                "sub_principles": [
                    {
                        "variation": "Variation name",
                        "description": "How this variation works",
                        "example": "Real example",
                        "when_to_use": "Appropriate situations"
                    },
                    ... (at least 3 variations)
                ],
                "selection_criteria": "Choose variation based on..."
            }
            """,
            why_this_matters=f"Understanding variations of Principle #{principle_num} helps select optimal approach for our specific constraints.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num} Variations",
        )

    elif step_num == 40:
        principle_num = accumulated_knowledge.get("step_37", {}).get(
            "principle_number", principles[1] if len(principles) > 1 else 15
        )
        principle_name = accumulated_knowledge.get("step_37", {}).get(
            "principle_name", f"Principle {principle_num}"
        )

        return StepInstruction(
            task=f"Apply Principle #{principle_num} ({principle_name}) to YOUR specific problem - generate concrete solution concepts",
            search_queries=[
                f"apply principle {principle_num} to {problem[:50]}",
                f"how to use {principle_name} for {problem[:50]}",
                f"principle {principle_num} solution examples similar problems",
                f"{principle_name} implementation engineering design",
            ],
            extract_requirements=[
                "solutions",  # Array of solution concept objects with concept/principle_application/how_it_works/expected_benefits/implementation/challenges/feasibility
            ],
            validation_criteria=f"Must generate at least 3 concrete solution concepts applying Principle #{principle_num} to the problem",
            expected_output_format="""
            {
                "solutions": [
                    {
                        "concept": "Solution concept name",
                        "principle_application": "How principle maps to problem",
                        "how_it_works": "Detailed explanation",
                        "expected_benefits": ["benefit1", "benefit2", "benefit3"],
                        "implementation": "How to build this",
                        "challenges": ["challenge1", "challenge2"],
                        "feasibility": "HIGH/MEDIUM/LOW - reasoning"
                    },
                    ... (at least 3 solutions)
                ]
            }
            """,
            why_this_matters=f"Applying Principle #{principle_num} may reveal different solutions than Principle from steps 33-36. TRIZ often combines multiple principles for best results.",
            related_triz_tool=f"40 Inventive Principles - Principle #{principle_num} Application",
        )

    elif step_num == 41:
        # Get third principle if exists
        principle_num = principles[2] if len(principles) > 2 else None

        if principle_num:
            return StepInstruction(
                task=f"Research Principle #{principle_num} (third recommended principle) if applicable",
                search_queries=[
                    f"TRIZ principle {principle_num} description application",
                    f"principle {principle_num} examples {problem[:50]}",
                    f"how to apply principle {principle_num}",
                    f"principle {principle_num} combined with other principles",
                ],
                extract_requirements=[
                    "principle_number",
                    "principle_name",
                    "principle_summary",
                    "quick_application_ideas",
                    "combination_potential",
                ],
                validation_criteria=f"Must research Principle #{principle_num} and identify at least 2 application ideas",
                expected_output_format=f"""
                {{
                    "principle_number": {principle_num},
                    "principle_name": "Name from research",
                    "summary": "Brief description of principle",
                    "application_ideas": [
                        "Idea 1 for our problem",
                        "Idea 2 for our problem"
                    ],
                    "combination_with_previous": "How this combines with principles from steps 33-40"
                }}
                """,
                why_this_matters=f"Contradiction Matrix recommended 3+ principles. Third principle often provides complementary approach to combine with first two.",
                related_triz_tool=f"40 Inventive Principles - Principle #{principle_num}",
            )
        else:
            # Skip if no third principle
            return StepInstruction(
                task="No third principle recommended - document principle application status",
                search_queries=[
                    "combining multiple TRIZ principles synergy",
                    "multi-principle solutions TRIZ",
                    "how to integrate TRIZ principles effectively",
                    "complementary TRIZ principles combinations",
                ],
                extract_requirements=[
                    "principles_applied",
                    "combination_opportunities",
                    "synergy_analysis",
                    "next_steps",
                ],
                validation_criteria="Document which principles were applied and potential combinations",
                expected_output_format="""
                {
                    "principles_applied": [1, 15],
                    "combinations_identified": "How principles 1 and 15 can work together",
                    "synergy_analysis": "Analysis of how principles complement each other",
                    "next_steps": "Proceed to Standard Solutions",
                    "status": "Only 2 principles recommended, proceeding to Standard Solutions"
                }
                """,
                why_this_matters="Documenting principle application status ensures we track all TRIZ tools used. Understanding synergies helps create better combined solutions.",
                related_triz_tool="40 Inventive Principles Summary",
            )

    elif step_num == 42:
        # Get top harmful function from step 21
        top_harm = harms[0] if harms else {"description": "primary harmful function"}

        return StepInstruction(
            task="Apply Standard Solution: ELIMINATE harmful function completely",
            search_queries=[
                f"eliminate harm {top_harm.get('description', '')[:40]} TRIZ",
                "standard solution eliminate harmful function",
                "trimming TRIZ remove component",
                f"remove eliminate {top_harm.get('description', '')[:40]}",
                "harm elimination engineering examples",
            ],
            extract_requirements=[
                "elimination_strategies",
                "trimming_candidates",
                "function_transfer_methods",
                "expected_outcomes",
                "feasibility_analysis",
            ],
            validation_criteria="Must propose at least 2 concrete methods to ELIMINATE the harmful function",
            expected_output_format="""
            {
                "harm_to_eliminate": "Description of harmful function from Step 21",
                "elimination_methods": [
                    {
                        "method": "Complete material substitution",
                        "how": "Replace aluminum with magnesium alloy - eliminates weight harm directly",
                        "function_transfer": "Structural function transfers to magnesium (same capability)",
                        "expected_result": "34% weight reduction, harm eliminated",
                        "challenges": ["Magnesium more expensive", "Requires different processing"],
                        "feasibility": "HIGH - automotive industry proven"
                    },
                    {
                        "method": "Trimming via redesign",
                        "how": "Eliminate entire component by transferring its function to existing parts",
                        "function_transfer": "Structural support transferred to chassis, mount transferred to base",
                        "expected_result": "100% elimination of component weight harm",
                        "challenges": ["Must verify chassis can handle load", "May need reinforcement"],
                        "feasibility": "MEDIUM - requires structural analysis"
                    }
                ]
            }
            """,
            why_this_matters="ELIMINATION is the most Ideal solution - completely removes the harm, increasing Ideality dramatically. Standard Solutions prioritize: Eliminate > Block > Convert > Correct.",
            related_triz_tool="76 Standard Solutions - Eliminate Harm + Trimming",
        )

    elif step_num == 43:
        top_harm = harms[0] if harms else {"description": "primary harmful function"}

        return StepInstruction(
            task="Apply Standard Solution: BLOCK harmful function (if elimination impossible)",
            search_queries=[
                f"block prevent {top_harm.get('description', '')[:40]}",
                "standard solution block harmful function TRIZ",
                "shielding blocking harm engineering",
                "prevent harm without removing source",
                "barrier protection harmful effect",
            ],
            extract_requirements=[
                "blocking_strategies",
                "barrier_methods",
                "isolation_techniques",
                "effectiveness_assessment",
            ],
            validation_criteria="Must propose at least 2 methods to BLOCK the harmful function if elimination not possible",
            expected_output_format="""
            {
                "harm_to_block": "Description of harm",
                "blocking_methods": [
                    {
                        "method": "Physical barrier/shield",
                        "how": "Add protective layer that blocks harm from reaching target",
                        "example": "Damping layer to block vibration, insulation to block heat",
                        "expected_result": "80-95% harm reduction",
                        "cost": "Lower than elimination but adds component",
                        "feasibility": "MEDIUM - adds weight/complexity"
                    },
                    {
                        "method": "Field-based blocking",
                        "how": "Use opposing field to counteract harmful field",
                        "example": "Active noise cancellation, counter-magnetic field",
                        "expected_result": "Variable - 60-99% depending on control",
                        "cost": "Requires energy and control system",
                        "feasibility": "LOW - complex but high-tech solution"
                    }
                ]
            }
            """,
            why_this_matters="If elimination impossible (step 42), blocking is next-best Standard Solution. Blocks harm path while keeping source.",
            related_triz_tool="76 Standard Solutions - Block Harm",
        )

    elif step_num == 44:
        top_harm = harms[0] if harms else {"description": "primary harmful function"}

        return StepInstruction(
            task="Apply Standard Solution: CONVERT harm to benefit (turn problem into opportunity)",
            search_queries=[
                f"convert {top_harm.get('description', '')[:40]} to benefit",
                "waste to value TRIZ standard solution",
                "turn harm into benefit engineering examples",
                "use waste byproduct problem as resource",
                "beneficial reuse harmful output",
            ],
            extract_requirements=[
                "conversion_strategies",
                "beneficial_uses",
                "value_creation_methods",
                "implementation_examples",
            ],
            validation_criteria="Must propose at least 2 methods to CONVERT the harm into something beneficial",
            expected_output_format="""
            {
                "harm_to_convert": "Description of harm",
                "conversion_methods": [
                    {
                        "method": "Use waste material for new function",
                        "how": "Repurpose waste aluminum from trimming/cutting as counterweight or heat sink",
                        "benefit_created": "Free material for another function + waste reduction",
                        "example": "Automotive uses stamping scrap as reinforcement panels",
                        "expected_value": "5-10% cost reduction + environmental benefit",
                        "feasibility": "HIGH - well-proven approach"
                    },
                    {
                        "method": "Exploit heavy weight as feature",
                        "how": "If weight can't be eliminated, USE it as: stability base, momentum flywheel, energy storage",
                        "benefit_created": "Weight becomes stabilizing feature instead of harm",
                        "example": "Heavy camera becomes steady-cam, wrecking ball uses weight as tool",
                        "expected_value": "Transforms harm into primary function",
                        "feasibility": "MEDIUM - requires paradigm shift in design"
                    }
                ]
            }
            """,
            why_this_matters="Converting harm to benefit is the most CREATIVE Standard Solution - increases Ideality by both reducing harms AND increasing benefits simultaneously.",
            related_triz_tool="76 Standard Solutions - Convert Harm to Good",
        )

    elif step_num == 45:
        top_insufficient = (
            insufficient[0]
            if insufficient
            else {"description": "insufficient function"}
        )

        return StepInstruction(
            task="Apply Standard Solution: ENHANCE insufficient functions (boost weak functions)",
            search_queries=[
                f"enhance improve {top_insufficient.get('description', '')[:40]}",
                "standard solution enhance insufficient function TRIZ",
                "amplify boost weak function engineering",
                "improve insufficient action",
                "strengthening weak functions examples",
            ],
            extract_requirements=[
                "enhancement_strategies",
                "amplification_methods",
                "boosting_techniques",
                "expected_improvements",
            ],
            validation_criteria="Must propose at least 3 methods to ENHANCE insufficient functions from Step 19",
            expected_output_format="""
            {
                "function_to_enhance": "Description of insufficient function from Step 19",
                "enhancement_methods": [
                    {
                        "method": "Add resources from environment",
                        "how": "Use freely available resources (gravity, air pressure, thermal) to boost function",
                        "example": "Use gravity assist for movement, ambient air for cooling",
                        "expected_improvement": "Function boosted 30-50% with zero added cost",
                        "feasibility": "HIGH - using free resources"
                    },
                    {
                        "method": "Field intensification",
                        "how": "Concentrate force/energy in smaller area or shorter time",
                        "example": "Pulse power instead of continuous, focus force to point not area",
                        "expected_improvement": "2-10x improvement in local intensity",
                        "feasibility": "MEDIUM - may require control systems"
                    },
                    {
                        "method": "Introduce intermediary",
                        "how": "Add intermediate object/substance that carries function more effectively",
                        "example": "Use lubricant for friction, catalyst for reaction, lever for force",
                        "expected_improvement": "Function efficiency +40-90%",
                        "feasibility": "MEDIUM - adds component but proven"
                    }
                ]
            }
            """,
            why_this_matters="Insufficient functions are opportunities - boosting them increases benefits in Ideality equation. Standard Solutions provide systematic approaches.",
            related_triz_tool="76 Standard Solutions - Enhance Insufficient Function",
        )

    elif step_num == 46:
        functions_needed = effects_needed or [
            {"function": "primary function needed", "x_factor": "system acts on object"}
        ]

        return StepInstruction(
            task="Research Effects Database for scientific/engineering effects to deliver needed functions",
            search_queries=[
                f"TRIZ effects database {functions_needed[0].get('function', '')[:40]}",
                f"physical effects achieve {functions_needed[0].get('function', '')[:40]}",
                f"scientific principles {functions_needed[0].get('function', '')[:40]}",
                "effects database X-Factor function delivery",
                "engineering effects catalog physics chemistry",
            ],
            extract_requirements=[
                "effects_found",
                "function_matching",
                "implementation_methods",
                "examples_applications",
            ],
            validation_criteria="Must find at least 3 scientific/engineering effects that deliver needed functions from Step 31",
            expected_output_format="""
            {
                "function_searches": [
                    {
                        "desired_function": "Heat material locally",
                        "x_factor": "System heats material",
                        "effects_found": [
                            {
                                "effect_name": "Induction heating",
                                "how_it_works": "Electromagnetic field induces eddy currents in conductive material, generating heat",
                                "applicability": "Works with metals (Al, Mg, steel), fast heating, localized control",
                                "implementation": "Induction coil around part, RF power supply, cooling system",
                                "example": "Induction brazing, heat treating, cookware",
                                "feasibility": "HIGH - well-proven for metal heating"
                            },
                            {
                                "effect_name": "Resistive heating",
                                "how_it_works": "Electrical current through resistive material generates Joule heat",
                                "applicability": "Simple, direct heating of conductive materials",
                                "implementation": "Electrodes contact material, power supply, temperature control",
                                "example": "Resistance spot welding, hot wire cutting",
                                "feasibility": "HIGH - simple and proven"
                            },
                            {
                                "effect_name": "Friction heating",
                                "how_it_works": "Mechanical friction converts kinetic energy to heat",
                                "applicability": "Tool-based heating, localized, no electrical needed",
                                "implementation": "Rotating tool, pressure application, controlled motion",
                                "example": "Friction stir welding, friction forming",
                                "feasibility": "MEDIUM - requires mechanical setup"
                            }
                        ]
                    }
                ]
            }
            """,
            why_this_matters="Effects Database connects desired FUNCTIONS to proven scientific METHODS to achieve them. This is how TRIZ accesses cross-domain knowledge - a physics effect from one field solves engineering problem in another.",
            related_triz_tool="TRIZ Effects Database (X-Factor: Subject-Action-Object)",
        )

    elif step_num == 47:
        # Check if materials problem detected
        materials_detected = (
            "material" in problem.lower() or "weight" in problem.lower()
        )

        return StepInstruction(
            task="DEEP materials research through engineering materials books (44+ books available)",
            search_queries=[
                f"materials properties {problem[:50]} engineering handbook",
                "lightweight materials comparison density strength",
                "aluminum magnesium carbon fiber CFRP titanium comparison",
                "formability of lightweight metals",
                "materials selection engineering design lightweight",
            ],
            extract_requirements=[
                "candidate_materials",
                "materials_properties_overview",
                "source_books",
                "comparative_analysis",
            ],
            validation_criteria="Must research at least 5 candidate materials from materials engineering books with property comparisons",
            expected_output_format="""
            {
                "materials_researched": [
                    {
                        "material": "Magnesium AZ31B alloy",
                        "why_candidate": "35% lighter than aluminum, good formability when heated",
                        "source_books": ["ASM Metals Handbook Vol 2", "Magnesium Technology"],
                        "properties_found": "Density ~1.77 g/cm³, tensile strength 200-290 MPa, excellent warm formability 200-300°C",
                        "applicability": "HIGH - direct aluminum replacement with weight savings"
                    },
                    {
                        "material": "Carbon Fiber Reinforced Polymer (CFRP)",
                        "why_candidate": "60% lighter than aluminum, 5x stronger",
                        "source_books": ["Composites Engineering Handbook", "Carbon Fiber Composites"],
                        "properties_found": "Density 1.5-1.6 g/cm³, tensile strength 600-1000 MPa, anisotropic properties",
                        "applicability": "MEDIUM - excellent properties but poor formability, requires layup/molding"
                    },
                    {
                        "material": "Aluminum-Lithium alloys (Al-Li)",
                        "why_candidate": "10% lighter than standard aluminum, better strength",
                        "source_books": ["ASM Specialty Handbook Aluminum", "Aerospace Materials"],
                        "properties_found": "Density 2.5 g/cm³ (vs 2.7 for Al), strength 450-550 MPa, good formability",
                        "applicability": "HIGH - aerospace proven, formability similar to aluminum"
                    },
                    {
                        "material": "Titanium alloys (Ti-6Al-4V)",
                        "why_candidate": "40% lighter than steel, extremely strong",
                        "source_books": ["Titanium: A Technical Guide", "ASM Metals Handbook"],
                        "properties_found": "Density 4.43 g/cm³, strength 900-1000 MPa, difficult to form",
                        "applicability": "LOW - heavier than Al/Mg, poor formability, expensive"
                    },
                    {
                        "material": "Glass Fiber Reinforced Polymer (GFRP)",
                        "why_candidate": "Lighter than aluminum, lower cost than CFRP",
                        "source_books": ["Composites Handbook", "Fiberglass Engineering"],
                        "properties_found": "Density 1.8-2.0 g/cm³, strength 200-400 MPa, moldable",
                        "applicability": "MEDIUM - moldable but requires tooling, less formable than metals"
                    }
                ]
            }
            """,
            why_this_matters="Deep materials research from 44+ engineering books provides authoritative data for materials selection. This is CRITICAL for materials-related problems - we need real engineering data, not generic descriptions.",
            related_triz_tool="Materials Database + Resources Thinking",
        )

    elif step_num == 48:
        return StepInstruction(
            task="Extract precise material properties: densities (g/cm³), strengths (MPa), formability characteristics",
            search_queries=[
                "material density table g/cm³ engineering materials",
                "tensile strength MPa materials comparison",
                "formability index metals warm cold forming",
                "materials properties numerical values handbook",
                "aluminum magnesium CFRP titanium properties table",
            ],
            extract_requirements=[
                "density_values",
                "strength_values",
                "formability_ratings",
                "manufacturing_properties",
                "source_verification",
            ],
            validation_criteria="Must extract precise numerical properties for all 5+ candidate materials from Step 47",
            expected_output_format="""
            {
                "materials_properties": [
                    {
                        "material": "Aluminum 6061-T6",
                        "density": {"value": 2.70, "unit": "g/cm³", "source": "ASM Metals Handbook"},
                        "tensile_strength": {"value": 310, "unit": "MPa", "source": "ASM Metals Handbook"},
                        "yield_strength": {"value": 276, "unit": "MPa", "source": "ASM Metals Handbook"},
                        "formability": {"rating": "EXCELLENT", "notes": "Cold formable, bends easily", "source": "Sheet Metal Forming Handbook"},
                        "elongation": {"value": 12, "unit": "%", "source": "ASM"},
                        "cost_relative": {"value": 1.0, "baseline": "Aluminum = 1.0"}
                    },
                    {
                        "material": "Magnesium AZ31B",
                        "density": {"value": 1.77, "unit": "g/cm³", "source": "Magnesium Technology 2020"},
                        "tensile_strength": {"value": 260, "unit": "MPa", "source": "Magnesium Technology"},
                        "yield_strength": {"value": 200, "unit": "MPa", "source": "Magnesium Technology"},
                        "formability": {"rating": "GOOD (warm)", "notes": "Excellent at 200-300°C, poor at room temp", "source": "Forming of Magnesium"},
                        "elongation": {"value": 15, "unit": "%", "source": "Magnesium Technology"},
                        "cost_relative": {"value": 3.5, "baseline": "3.5x aluminum cost"}
                    },
                    ... (continue for all 5+ materials)
                ]
            }
            """,
            why_this_matters="Precise numerical properties enable quantitative comparison and engineering calculations. Density drives weight, strength drives sizing, formability drives manufacturing feasibility.",
            related_triz_tool="Materials Database - Property Extraction",
        )

    elif step_num == 49:
        return StepInstruction(
            task="Create material comparison tables: weight vs aluminum %, strength-to-weight ratios, formability rankings",
            search_queries=[
                "materials comparison table weight strength",
                "specific strength materials ranking",
                "weight reduction percentage aluminum alternatives",
                "materials selection chart ashby",
                "formability ranking metals polymers composites",
            ],
            extract_requirements=[
                "comparison_tables",
                "weight_calculations",
                "strength_to_weight_ratios",
                "formability_rankings",
                "recommendations",
            ],
            validation_criteria="Must create comparison table for all 5+ materials showing weight %, strength/weight, formability, cost",
            expected_output_format="""
            {
                "weight_comparison_table": [
                    {"material": "Aluminum 6061-T6", "density": 2.70, "weight_vs_al": "100% (baseline)", "weight_reduction": "0%"},
                    {"material": "Magnesium AZ31B", "density": 1.77, "weight_vs_al": "65.6%", "weight_reduction": "34.4%"},
                    {"material": "CFRP", "density": 1.55, "weight_vs_al": "57.4%", "weight_reduction": "42.6%"},
                    {"material": "Al-Li alloy", "density": 2.50, "weight_vs_al": "92.6%", "weight_reduction": "7.4%"},
                    {"material": "Titanium Ti-6Al-4V", "density": 4.43, "weight_vs_al": "164%", "weight_reduction": "-64% (heavier)"}
                ],
                "strength_to_weight_table": [
                    {"material": "Aluminum 6061-T6", "strength": 310, "density": 2.70, "specific_strength": 114.8, "ranking": 4},
                    {"material": "Magnesium AZ31B", "strength": 260, "density": 1.77, "specific_strength": 146.9, "ranking": 3},
                    {"material": "CFRP", "strength": 800, "density": 1.55, "specific_strength": 516.1, "ranking": 1},
                    {"material": "Al-Li alloy", "strength": 500, "density": 2.50, "specific_strength": 200.0, "ranking": 2},
                    {"material": "Titanium Ti-6Al-4V", "strength": 950, "density": 4.43, "specific_strength": 214.4, "ranking": 2}
                ],
                "formability_rankings": [
                    {"rank": 1, "material": "Aluminum 6061-T6", "formability": "Excellent cold", "notes": "Easiest to form"},
                    {"rank": 2, "material": "Magnesium AZ31B", "formability": "Excellent warm (200-300°C)", "notes": "Requires heating"},
                    {"rank": 3, "material": "Al-Li alloy", "formability": "Good", "notes": "Similar to aluminum"},
                    {"rank": 4, "material": "Titanium", "formability": "Poor", "notes": "Difficult, requires high temp"},
                    {"rank": 5, "material": "CFRP", "formability": "Not formable", "notes": "Must be molded/laid up"}
                ],
                "cost_comparison": [
                    {"material": "Aluminum 6061-T6", "relative_cost": 1.0, "$/kg": 3.50},
                    {"material": "Magnesium AZ31B", "relative_cost": 3.5, "$/kg": 12.25},
                    {"material": "CFRP", "relative_cost": 15.0, "$/kg": 52.50},
                    {"material": "Al-Li alloy", "relative_cost": 8.0, "$/kg": 28.00},
                    {"material": "Titanium", "relative_cost": 20.0, "$/kg": 70.00}
                ],
                "recommendations": {
                    "best_weight_reduction": {"material": "CFRP", "reduction": "42.6%", "caveat": "Not formable, expensive"},
                    "best_formability_vs_weight": {"material": "Magnesium AZ31B", "reduction": "34.4%", "caveat": "Requires warm forming"},
                    "best_cost_vs_weight": {"material": "Magnesium AZ31B", "reduction": "34.4%", "cost_increase": "3.5x"},
                    "optimal_choice": "Magnesium AZ31B - best balance of weight reduction (34%), formability (excellent warm), and reasonable cost increase"
                }
            }
            """,
            why_this_matters="Comparison tables transform raw data into decision support. Side-by-side comparison reveals trade-offs and optimal choices based on Ideality (benefits vs costs vs harms).",
            related_triz_tool="Materials Selection + Ideality-Based Ranking",
        )

    elif step_num == 50:
        return StepInstruction(
            task="Synthesize ALL findings from steps 33-49 into complete, integrated solution concepts",
            search_queries=[
                "combine multiple TRIZ principles integrated solution",
                "multi-principle solutions TRIZ case studies",
                f"complete solution concept {problem[:50]}",
                "integrating principles standard solutions materials",
            ],
            extract_requirements=[
                "integrated_solutions",
                "triz_tools_combined",
                "expected_ideality_improvement",
                "implementation_roadmap",
                "risk_assessment",
            ],
            validation_criteria="Must create at least 3 complete solution concepts that INTEGRATE multiple TRIZ tools from previous steps",
            expected_output_format="""
            {
                "complete_solutions": [
                    {
                        "solution_name": "Modular Magnesium Segments with Induction Heating",
                        "description": "Segmented structure using magnesium AZ31B with snap-fit assembly and integrated induction heating for warm forming",
                        "triz_tools_integrated": [
                            {"tool": "Principle 1 (Segmentation)", "application": "5 modular segments with standard interfaces"},
                            {"tool": "Principle 15 (Dynamism)", "application": "Adjustable segments adapt to needs"},
                            {"tool": "Standard Solution: Eliminate harm", "application": "Magnesium eliminates 34% weight"},
                            {"tool": "Effects Database: Induction heating", "application": "Local heating enables warm forming"},
                            {"tool": "Materials: Magnesium AZ31B", "application": "Direct aluminum replacement"}
                        ],
                        "expected_benefits": [
                            "34.4% weight reduction (magnesium vs aluminum)",
                            "Modular design enables easy repair/replacement",
                            "Formability maintained via induction heating",
                            "Customization via segment swapping"
                        ],
                        "expected_costs": [
                            "Magnesium material 3.5x aluminum cost",
                            "Induction heating system cost",
                            "Warm forming process adds cycle time",
                            "Module design/tooling investment"
                        ],
                        "expected_harms_eliminated": [
                            "Weight harm reduced 34%",
                            "Formability harm eliminated via heating",
                            "Modularity reduces maintenance downtime"
                        ],
                        "ideality_calculation": {
                            "current_ideality": 0.90,
                            "projected_ideality": 1.85,
                            "improvement": "+105%"
                        },
                        "implementation_plan": {
                            "phase1": "Design modular interfaces and segment geometry",
                            "phase2": "Prototype induction heating system for magnesium",
                            "phase3": "Test warm forming process parameters",
                            "phase4": "Manufacture and test individual modules",
                            "phase5": "Integration and system validation"
                        },
                        "risks": [
                            {"risk": "Magnesium corrosion in humid environments", "mitigation": "Anodizing or coating"},
                            {"risk": "Snap-fit strength under load", "mitigation": "FEA validation, mechanical backup"},
                            {"risk": "Induction heating complexity", "mitigation": "Partner with heating equipment supplier"}
                        ],
                        "feasibility": "HIGH - all technologies proven individually, integration is innovation"
                    },
                    {
                        "solution_name": "Aluminum-CFRP Hybrid Segmented Structure",
                        "description": "Multi-material segmented design: CFRP for low-stress areas (40% weight), aluminum for high-stress areas (60% weight)",
                        "triz_tools_integrated": [
                            {"tool": "Principle 1 (Segmentation)", "application": "Segment by stress zones"},
                            {"tool": "Principle 40 (Composite materials)", "application": "Hybrid Al-CFRP combination"},
                            {"tool": "Standard Solution: Convert harm", "application": "Use CFRP molding constraint as design feature"},
                            {"tool": "Materials: CFRP + Aluminum", "application": "Best material per zone"}
                        ],
                        "expected_benefits": [
                            "25-30% total weight reduction",
                            "Aluminum zones remain easily formable",
                            "CFRP provides high strength-to-weight where needed",
                            "Differentiated material costs per zone"
                        ],
                        "ideality_calculation": {
                            "current_ideality": 0.90,
                            "projected_ideality": 1.45,
                            "improvement": "+61%"
                        },
                        "implementation_plan": "FEA stress analysis → zone definition → CFRP molding design → aluminum forming → joining method selection → prototype",
                        "risks": [
                            {"risk": "Thermal expansion mismatch Al-CFRP", "mitigation": "Flexible joints, analysis"},
                            {"risk": "Joining dissimilar materials", "mitigation": "Mechanical fasteners + adhesive hybrid"}
                        ],
                        "feasibility": "MEDIUM-HIGH - automotive proven, requires multi-material expertise"
                    },
                    {
                        "solution_name": "Pure Aluminum with Honeycomb Core Segmentation",
                        "description": "Keep aluminum but segment solid sheet into honeycomb/lattice structure - maintain forming, halve weight",
                        "triz_tools_integrated": [
                            {"tool": "Principle 1 (Segmentation - fragmentation variant)", "application": "Honeycomb internal structure"},
                            {"tool": "Standard Solution: Eliminate harm", "application": "Remove 50% of material mass"},
                            {"tool": "Principle 3 (Local quality)", "application": "Solid skin, hollow core"},
                            {"tool": "Materials: Keep aluminum", "application": "Maintain formability advantage"}
                        ],
                        "expected_benefits": [
                            "40-50% weight reduction",
                            "Maintains aluminum formability",
                            "Better energy absorption",
                            "Proven aerospace technology"
                        ],
                        "ideality_calculation": {
                            "current_ideality": 0.90,
                            "projected_ideality": 1.60,
                            "improvement": "+78%"
                        },
                        "implementation_plan": "Honeycomb core sourcing → face sheet forming → adhesive bonding → edge sealing → validation",
                        "risks": [
                            {"risk": "Forming honeycomb panels into curves difficult", "mitigation": "Pre-form before bonding OR use flexible honeycomb"},
                            {"risk": "Higher piece-part cost vs solid sheet", "mitigation": "Offset by weight savings value"}
                        ],
                        "feasibility": "HIGH - aerospace standard, suppliers available"
                    }
                ],
                "recommendation": "Solution 1 (Modular Magnesium) offers highest Ideality improvement (+105%) and addresses all contradictions. Solution 3 (Honeycomb Aluminum) is lower-risk alternative if magnesium expertise unavailable."
            }
            """,
            why_this_matters="This synthesis step is WHERE TRIZ DELIVERS VALUE - combining multiple principles, Standard Solutions, materials research, and effects into complete, implementable solutions that dramatically increase Ideality.",
            related_triz_tool="Complete TRIZ Methodology - Synthesis of All Tools",
        )

    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 5 (valid: 33-50)")
