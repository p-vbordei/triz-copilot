"""
PHASE 6: RANK & IMPLEMENT (Steps 51-60)

Evaluate all solution concepts using Ideality.
Rank solutions on Ideality Plot.
Create implementation plan.

Steps:
51. Calculate Ideality for each solution concept
52. Calculate expected benefits for each solution
53. Calculate expected costs for each solution
54. Calculate expected harms for each solution
55. Create Ideality Plot with all solutions
56. Categorize solutions (Implement Now, Improve, Research, Park)
57. Select top 3 solutions for implementation
58. Research implementation requirements (suppliers, tech, resources)
59. Create detailed implementation timeline
60. Generate final synthesis with complete evidence
"""

from typing import Dict, Any
from ..triz_models import StepInstruction


def generate(
    step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
) -> StepInstruction:
    """Generate instruction for Phase 6 steps"""

    # Get solution concepts from step 50
    solutions = accumulated_knowledge.get("step_50", {}).get("complete_solutions", [])
    num_solutions = len(solutions) if solutions else 3

    if step_num == 51:
        return StepInstruction(
            task="Calculate Ideality score for EACH solution concept using TRIZ Ideality equation",
            search_queries=[
                "ideality calculation formula TRIZ benefits costs harms",
                "evaluate solution concepts ideality metric",
                "how to score solutions ideality equation",
                "ideality rating system TRIZ methodology",
            ],
            extract_requirements=[
                "solution_evaluations",  # Ideality for each solution
                "calculation_method",  # How calculated
                "ideality_scores",  # Numerical scores
                "ranking_order",  # Solutions ranked by Ideality
            ],
            validation_criteria=f"Must calculate Ideality for ALL {num_solutions} solution concepts from Step 50",
            expected_output_format="""
            {
                "ideality_formula": "Ideality = Sum(Benefits) / (Sum(Costs) + Sum(Harms))",
                "evaluations": [
                    {
                        "solution": "Modular Magnesium Segments with Induction Heating",
                        "benefits_sum": 47.5,
                        "costs_sum": 18.0,
                        "harms_sum": 8.5,
                        "ideality_score": 1.79,
                        "category": "EXCELLENT",
                        "vs_current": "+99% improvement from current 0.90"
                    },
                    {
                        "solution": "Aluminum-CFRP Hybrid Segmented Structure",
                        "benefits_sum": 42.0,
                        "costs_sum": 22.0,
                        "harms_sum": 11.0,
                        "ideality_score": 1.27,
                        "category": "GOOD",
                        "vs_current": "+41% improvement"
                    },
                    {
                        "solution": "Aluminum with Honeycomb Core",
                        "benefits_sum": 44.0,
                        "costs_sum": 16.0,
                        "harms_sum": 12.0,
                        "ideality_score": 1.57,
                        "category": "EXCELLENT",
                        "vs_current": "+74% improvement"
                    }
                ],
                "ranking": [
                    "1st: Modular Magnesium (1.79)",
                    "2nd: Honeycomb Aluminum (1.57)",
                    "3rd: Al-CFRP Hybrid (1.27)"
                ]
            }
            """,
            why_this_matters="Ideality score is THE metric for ranking solutions in TRIZ. Highest Ideality = best solution. This quantifies which solution provides most benefits with least costs and harms.",
            related_triz_tool="Ideality Equation",
        )

    elif step_num == 52:
        return StepInstruction(
            task="Calculate expected benefits for each solution - detailed breakdown with ratings",
            search_queries=[
                "quantify benefits solution concepts",
                "rate importance benefits 1-10 scale",
                "expected outcomes value proposition",
                f"benefits assessment {problem[:50]}",
            ],
            extract_requirements=[
                "benefits_per_solution",
                "importance_ratings",
                "achievement_estimates",
                "benefit_scoring",
            ],
            validation_criteria=f"Must identify and rate all benefits for each of {num_solutions} solutions",
            expected_output_format="""
            {
                "solutions_benefits": [
                    {
                        "solution": "Modular Magnesium Segments",
                        "benefits": [
                            {
                                "benefit": "Weight reduction 34%",
                                "importance": 10,
                                "achievement_level": 9,
                                "score": 9.0,
                                "evidence": "Magnesium density 1.77 vs aluminum 2.70 g/cm³"
                            },
                            {
                                "benefit": "Easy repair/replacement via modules",
                                "importance": 7,
                                "achievement_level": 9,
                                "score": 6.3,
                                "evidence": "Snap-fit modular design proven in consumer electronics"
                            },
                            {
                                "benefit": "Customization flexibility",
                                "importance": 6,
                                "achievement_level": 8,
                                "score": 4.8,
                                "evidence": "Modules can be swapped for different configurations"
                            },
                            {
                                "benefit": "Formability maintained",
                                "importance": 8,
                                "achievement_level": 8,
                                "score": 6.4,
                                "evidence": "Induction heating enables warm forming of magnesium"
                            },
                            {
                                "benefit": "Improved user mobility",
                                "importance": 9,
                                "achievement_level": 9,
                                "score": 8.1,
                                "evidence": "34% lighter = easier to carry/move"
                            }
                        ],
                        "total_benefit_score": 34.6
                    },
                    ... (for each solution)
                ]
            }
            """,
            why_this_matters="Benefits are the NUMERATOR in Ideality equation. Detailed scoring reveals which solution delivers most value. Importance × Achievement gives weighted benefit score.",
            related_triz_tool="Ideality Equation - Benefits Analysis",
        )

    elif step_num == 53:
        return StepInstruction(
            task="Calculate expected costs for each solution - money, time, materials, effort, energy",
            search_queries=[
                "cost estimation engineering solutions",
                "manufacturing costs materials processing",
                f"implementation costs {problem[:50]}",
                "resource requirements time money effort",
            ],
            extract_requirements=[
                "costs_per_solution",
                "cost_types",
                "magnitude_ratings",
                "cost_scoring",
            ],
            validation_criteria=f"Must identify and rate all costs for each of {num_solutions} solutions across cost types",
            expected_output_format="""
            {
                "solutions_costs": [
                    {
                        "solution": "Modular Magnesium Segments",
                        "costs": [
                            {
                                "cost": "Magnesium material",
                                "type": "money",
                                "magnitude": 7,
                                "score": 7.0,
                                "evidence": "Magnesium 3.5x cost of aluminum, but less total material"
                            },
                            {
                                "cost": "Induction heating system",
                                "type": "money",
                                "magnitude": 6,
                                "score": 6.0,
                                "evidence": "Induction coil + power supply ~$15k-25k"
                            },
                            {
                                "cost": "Warm forming cycle time",
                                "type": "time",
                                "magnitude": 5,
                                "score": 5.0,
                                "evidence": "Heating adds 30-60 seconds per part"
                            },
                            {
                                "cost": "Module design engineering",
                                "type": "effort",
                                "magnitude": 7,
                                "score": 7.0,
                                "evidence": "Interface design, snap-fit validation requires 200-300 engineering hours"
                            },
                            {
                                "cost": "Heating energy consumption",
                                "type": "energy",
                                "magnitude": 4,
                                "score": 4.0,
                                "evidence": "Induction heating 5-10 kW for 1 min per part"
                            }
                        ],
                        "total_cost_score": 29.0
                    },
                    ... (for each solution)
                ]
            }
            """,
            why_this_matters="Costs are in DENOMINATOR of Ideality. Lower costs = higher Ideality. Must capture ALL cost types: money, time, materials, effort, energy.",
            related_triz_tool="Ideality Equation - Costs Analysis",
        )

    elif step_num == 54:
        return StepInstruction(
            task="Calculate expected harms for each solution - safety, environmental, waste, side-effects",
            search_queries=[
                "potential problems risks solutions",
                "side effects unintended consequences",
                "environmental impact safety concerns",
                f"risks harms {problem[:50]}",
            ],
            extract_requirements=[
                "harms_per_solution",
                "harm_types",
                "severity_ratings",
                "harm_scoring",
            ],
            validation_criteria=f"Must identify and rate all potential harms for each of {num_solutions} solutions",
            expected_output_format="""
            {
                "solutions_harms": [
                    {
                        "solution": "Modular Magnesium Segments",
                        "harms": [
                            {
                                "harm": "Magnesium corrosion risk",
                                "type": "reliability",
                                "severity": 6,
                                "score": 6.0,
                                "evidence": "Magnesium corrodes in humid environments without coating",
                                "mitigation": "Anodizing or protective coating reduces to severity 2"
                            },
                            {
                                "harm": "Snap-fit potential failure under shock loads",
                                "type": "safety",
                                "severity": 5,
                                "score": 5.0,
                                "evidence": "Snap-fits can disengage under impact",
                                "mitigation": "Secondary mechanical locking or adhesive backup"
                            },
                            {
                                "harm": "Manufacturing complexity",
                                "type": "production",
                                "severity": 4,
                                "score": 4.0,
                                "evidence": "More parts = more assembly steps",
                                "mitigation": "Design for assembly minimizes impact"
                            },
                            {
                                "harm": "Magnesium fire risk during machining",
                                "type": "safety",
                                "severity": 3,
                                "score": 3.0,
                                "evidence": "Magnesium chips ignitable but controlled with coolant",
                                "mitigation": "Proper machining practices eliminate risk"
                            }
                        ],
                        "total_harm_score": 18.0,
                        "harm_score_with_mitigation": 8.0
                    },
                    ... (for each solution)
                ]
            }
            """,
            why_this_matters="Harms are in DENOMINATOR of Ideality. Identifying harms early allows mitigation planning. Even good solutions have harms - the key is minimizing them.",
            related_triz_tool="Ideality Equation - Harms Analysis",
        )

    elif step_num == 55:
        return StepInstruction(
            task="Create Ideality Plot visualizing all solutions on 2D graph: Ideality vs Feasibility",
            search_queries=[
                "ideality plot TRIZ visualization",
                "solution ranking chart benefits costs",
                "feasibility vs ideality matrix",
            ],
            extract_requirements=[
                "plot_coordinates",
                "quadrant_definitions",
                "solution_positioning",
                "visual_insights",
            ],
            validation_criteria=f"Must plot all {num_solutions} solutions on Ideality-Feasibility axes with quadrant categorization",
            expected_output_format="""
            {
                "ideality_plot": {
                    "x_axis": "Feasibility (0-10 scale)",
                    "y_axis": "Ideality Score (0-3.0 scale)",
                    "quadrants": {
                        "Q1_high_ideality_high_feasibility": {
                            "name": "IMPLEMENT NOW",
                            "description": "High Ideality + Easy to implement = DO THESE FIRST",
                            "solutions": ["Honeycomb Aluminum (1.57, 8.5)"]
                        },
                        "Q2_high_ideality_low_feasibility": {
                            "name": "RESEARCH & DEVELOP",
                            "description": "High Ideality but difficult = Worth additional TRIZ iteration",
                            "solutions": ["Modular Magnesium (1.79, 6.5)"]
                        },
                        "Q3_low_ideality_low_feasibility": {
                            "name": "PARK/DISCARD",
                            "description": "Low Ideality + Difficult = Not worth pursuing",
                            "solutions": []
                        },
                        "Q4_low_ideality_high_feasibility": {
                            "name": "IMPROVE OR SKIP",
                            "description": "Easy but low value = May need enhancement",
                            "solutions": ["Al-CFRP Hybrid (1.27, 7.0)"]
                        }
                    },
                    "plot_data": [
                        {"solution": "Modular Magnesium", "ideality": 1.79, "feasibility": 6.5, "quadrant": "Q2"},
                        {"solution": "Honeycomb Aluminum", "ideality": 1.57, "feasibility": 8.5, "quadrant": "Q1"},
                        {"solution": "Al-CFRP Hybrid", "ideality": 1.27, "feasibility": 7.0, "quadrant": "Q4"}
                    ],
                    "threshold_lines": {
                        "ideality_threshold": 1.2,
                        "feasibility_threshold": 6.0
                    }
                },
                "insights": [
                    "Honeycomb Aluminum in Q1 (Implement Now) - highest feasibility, good Ideality",
                    "Modular Magnesium in Q2 (Research) - highest Ideality but needs development",
                    "Al-CFRP Hybrid in Q4 (Improve) - feasible but needs Ideality boost"
                ]
            }
            """,
            why_this_matters="Ideality Plot VISUALIZES decision-making. It reveals which solutions to implement immediately (Q1), which need more work (Q2), which to improve (Q4), and which to discard (Q3).",
            related_triz_tool="Ideality Plot",
        )

    elif step_num == 56:
        return StepInstruction(
            task="Categorize all solutions into 4 decision categories based on Ideality Plot",
            search_queries=[
                "TRIZ solution categorization decision matrix",
                "implement now vs research vs improve TRIZ",
                "solution prioritization methodology",
            ],
            extract_requirements=[
                "category_assignments",
                "decision_rationale",
                "action_plans",
                "priorities",
            ],
            validation_criteria=f"Must categorize all {num_solutions} solutions with clear rationale and next actions",
            expected_output_format="""
            {
                "categories": {
                    "implement_now": {
                        "description": "High Ideality + High Feasibility → Implement immediately",
                        "solutions": [
                            {
                                "solution": "Honeycomb Aluminum Structure",
                                "ideality": 1.57,
                                "feasibility": 8.5,
                                "rationale": "74% Ideality improvement, proven aerospace technology, suppliers available, aluminum formability maintained",
                                "action": "Proceed to detailed design and prototyping",
                                "timeline": "3-6 months to production",
                                "risk": "LOW"
                            }
                        ]
                    },
                    "further_triz": {
                        "description": "High benefits but big problems → Run through TRIZ again to overcome barriers",
                        "solutions": [
                            {
                                "solution": "Modular Magnesium Segments",
                                "ideality": 1.79,
                                "feasibility": 6.5,
                                "rationale": "Highest Ideality (+99%) but challenges: magnesium expertise, induction heating integration, snap-fit validation",
                                "action": "Apply TRIZ to solve: (1) magnesium corrosion, (2) snap-fit reliability, (3) warm forming process",
                                "timeline": "6-12 months with additional TRIZ iteration",
                                "risk": "MEDIUM"
                            }
                        ]
                    },
                    "improve": {
                        "description": "Low benefits → Enhance or combine with other solutions",
                        "solutions": [
                            {
                                "solution": "Al-CFRP Hybrid",
                                "ideality": 1.27,
                                "feasibility": 7.0,
                                "rationale": "Feasible but Ideality only +41%, lower than alternatives",
                                "action": "Combine with segmentation principle more aggressively OR use as fallback if magnesium fails",
                                "timeline": "Consider as backup plan",
                                "risk": "LOW (backup option)"
                            }
                        ]
                    },
                    "park": {
                        "description": "Keep for future consideration but not current priority",
                        "solutions": []
                    }
                },
                "priority_order": [
                    "1st priority: Implement Honeycomb Aluminum (lowest risk, good Ideality)",
                    "2nd priority: Parallel TRIZ iteration on Modular Magnesium (highest Ideality potential)",
                    "3rd priority: Keep Al-CFRP Hybrid as backup"
                ]
            }
            """,
            why_this_matters="Categorization transforms analysis into ACTION. It tells us exactly what to do: implement, research more, improve, or park. This is where TRIZ becomes operational.",
            related_triz_tool="Ideality Plot + Decision Framework",
        )

    elif step_num == 57:
        return StepInstruction(
            task="Select top 3 solutions for detailed implementation planning with full justification",
            search_queries=[
                "solution selection criteria engineering",
                "multi-criteria decision making",
                "pros cons analysis implementation",
            ],
            extract_requirements=[
                "selected_solutions",
                "selection_justification",
                "comparative_analysis",
                "implementation_strategy",
            ],
            validation_criteria="Must select top 3 solutions with detailed pros/cons and implementation strategy for each",
            expected_output_format="""
            {
                "selected_solutions": [
                    {
                        "rank": 1,
                        "solution": "Honeycomb Aluminum Structure",
                        "selection_rationale": "RECOMMENDED PRIMARY SOLUTION - Best balance of Ideality improvement (74%), feasibility (8.5/10), and risk (LOW)",
                        "pros": [
                            "Proven aerospace technology with established suppliers",
                            "40-50% weight reduction achievable",
                            "Maintains aluminum formability advantage",
                            "Lower risk than magnesium or composites",
                            "Cost increase moderate (honeycomb core pricing competitive)"
                        ],
                        "cons": [
                            "Forming honeycomb panels into curves challenging (but solvable)",
                            "Higher piece-part cost than solid sheet (but total cost lower due to weight savings)",
                            "Edge sealing required (standard practice)"
                        ],
                        "why_best": "Delivers substantial weight reduction with proven technology. Lowest risk path to 74% Ideality improvement.",
                        "implementation_approach": "Parallel path: (1) Source honeycomb core suppliers, (2) Design face sheet geometry, (3) Develop bonding process, (4) Prototype & test"
                    },
                    {
                        "rank": 2,
                        "solution": "Modular Magnesium Segments with Induction Heating",
                        "selection_rationale": "RECOMMENDED R&D TRACK - Highest Ideality potential (99% improvement) worth additional development",
                        "pros": [
                            "Highest Ideality improvement of all solutions (+99%)",
                            "34% weight reduction from material substitution alone",
                            "Modular design enables customization, easy repair",
                            "Induction heating solves formability contradiction",
                            "Innovation differentiator vs competitors"
                        ],
                        "cons": [
                            "Magnesium expertise required (partner or hire)",
                            "Corrosion concerns need coating solution",
                            "Snap-fit design requires validation",
                            "Warm forming process development needed",
                            "Higher material cost (3.5x aluminum)"
                        ],
                        "why_best": "Highest performance potential. Worth parallel development track given upside.",
                        "implementation_approach": "Phase 1: Apply TRIZ to solve corrosion+snap-fit challenges. Phase 2: Prototype single module. Phase 3: Validate warm forming. Phase 4: System integration"
                    },
                    {
                        "rank": 3,
                        "solution": "Al-CFRP Hybrid Segmented Structure",
                        "selection_rationale": "BACKUP SOLUTION - Moderate Ideality (+41%) but valuable as fallback if primary options fail",
                        "pros": [
                            "Multi-material optimization proven in automotive",
                            "25-30% weight reduction",
                            "Aluminum zones maintain formability",
                            "CFRP provides high strength-to-weight where needed"
                        ],
                        "cons": [
                            "Thermal expansion mismatch between Al-CFRP",
                            "Joining dissimilar materials complex",
                            "CFRP cost high (15x aluminum)",
                            "Lower Ideality than alternatives"
                        ],
                        "why_best": "Solid backup if magnesium or honeycomb prove infeasible. Automotive-proven approach.",
                        "implementation_approach": "Keep as contingency. Minimal investment unless primary solutions blocked."
                    }
                ],
                "overall_strategy": "Implement Solution 1 (Honeycomb) as primary production path. Parallel R&D on Solution 2 (Magnesium) for next-generation. Hold Solution 3 (Hybrid) as backup.",
                "resource_allocation": {
                    "honeycomb_aluminum": "70% resources - production focus",
                    "modular_magnesium": "25% resources - R&D track",
                    "al_cfrp_hybrid": "5% resources - monitoring/contingency"
                }
            }
            """,
            why_this_matters="Final solution selection is critical decision point. Must balance Ideality, feasibility, risk, and resources. Top 3 approach provides primary + backup + innovation track.",
            related_triz_tool="Decision Making + Ideality-Based Selection",
        )

    elif step_num == 58:
        top_solution = accumulated_knowledge.get("step_57", {}).get(
            "selected_solutions", [{}]
        )[0]
        solution_name = top_solution.get("solution", "primary solution")

        return StepInstruction(
            task=f"Research implementation requirements for {solution_name}: suppliers, technologies, resources, costs",
            search_queries=[
                f"suppliers {solution_name[:40]} manufacturing",
                f"equipment needed {solution_name[:40]} production",
                f"cost estimation {solution_name[:40]} implementation",
                f"technical requirements {solution_name[:40]}",
                "lead times manufacturing suppliers",
            ],
            extract_requirements=[
                "supplier_information",
                "technology_requirements",
                "resource_needs",
                "cost_estimates",
                "lead_times",
            ],
            validation_criteria="Must identify specific suppliers, equipment, costs, and lead times for top solution",
            expected_output_format="""
            {
                "solution": "Honeycomb Aluminum Structure",
                "suppliers": [
                    {
                        "category": "Honeycomb core",
                        "suppliers": ["Hexcel", "Plascore", "Gill Corporation", "Tubus Bauer"],
                        "recommended": "Hexcel - largest honeycomb supplier, aerospace quality",
                        "products": "Aluminum honeycomb 1/8\" - 1\" cell sizes, various densities",
                        "pricing": "$15-45 per sq ft depending on cell size/density",
                        "lead_time": "4-6 weeks for standard sizes, 8-12 weeks custom"
                    },
                    {
                        "category": "Adhesive bonding",
                        "suppliers": ["3M", "Henkel Loctite", "Cytec"],
                        "recommended": "3M AF-163 film adhesive - aerospace standard",
                        "pricing": "$8-12 per sq ft",
                        "lead_time": "2-4 weeks"
                    },
                    {
                        "category": "Aluminum face sheets",
                        "suppliers": ["Alcoa", "Kaiser Aluminum", "Novelis"],
                        "recommended": "Kaiser - good formability grades",
                        "products": "6061-T6 sheet 0.020\" - 0.125\" thick",
                        "pricing": "$3-5 per lb",
                        "lead_time": "1-2 weeks"
                    }
                ],
                "equipment_needed": [
                    {
                        "equipment": "Vacuum bagging setup for bonding",
                        "cost": "$5k-15k",
                        "supplier": "Airtech International, Richmond Aircraft",
                        "purpose": "Apply uniform pressure during adhesive cure"
                    },
                    {
                        "equipment": "Autoclave or oven (if not available)",
                        "cost": "$50k-200k (autoclave) or $10k-30k (oven)",
                        "supplier": "ASC Process Systems, Thermal Equipment",
                        "purpose": "Cure adhesive at 250-350°F"
                    },
                    {
                        "equipment": "CNC router for edge trimming",
                        "cost": "$25k-75k (or use existing)",
                        "supplier": "Haas, AXYZ, MultiCam",
                        "purpose": "Trim honeycomb panel edges cleanly"
                    }
                ],
                "technical_expertise": [
                    {
                        "skill": "Composite bonding techniques",
                        "source": "Hire composites technician OR train existing staff",
                        "timeline": "2-4 weeks training OR 4-6 weeks hiring"
                    },
                    {
                        "skill": "Honeycomb panel design",
                        "source": "Consultant from aerospace industry",
                        "timeline": "2-3 weeks consulting engagement"
                    }
                ],
                "total_cost_estimate": {
                    "materials_per_unit": "$150-300 (depending on panel size)",
                    "equipment_capital": "$40k-120k (one-time)",
                    "tooling_fixtures": "$15k-30k (one-time)",
                    "training_consulting": "$10k-20k (one-time)",
                    "total_startup": "$65k-170k",
                    "per_unit_manufacturing": "$180-350 (materials + labor + overhead)"
                },
                "lead_time_summary": {
                    "supplier_qualification": "2-4 weeks",
                    "equipment_procurement": "6-12 weeks",
                    "process_development": "4-8 weeks",
                    "first_prototype": "12-16 weeks from start"
                }
            }
            """,
            why_this_matters="Implementation requires REAL suppliers, equipment, and costs. This step grounds TRIZ solution in practical reality - can we actually build this?",
            related_triz_tool="Implementation Planning - Resources Analysis",
        )

    elif step_num == 59:
        solution_name = (
            accumulated_knowledge.get("step_57", {})
            .get("selected_solutions", [{}])[0]
            .get("solution", "primary solution")
        )

        return StepInstruction(
            task=f"Create detailed implementation timeline with phases, milestones, and resource allocation",
            search_queries=[
                "project timeline implementation phases",
                "product development schedule milestones",
                f"manufacturing timeline {solution_name[:40]}",
                "prototype to production timeline",
            ],
            extract_requirements=[
                "timeline_phases",
                "milestones",
                "resource_allocation",
                "risk_mitigation_schedule",
            ],
            validation_criteria="Must create complete timeline from design to production with specific durations and deliverables",
            expected_output_format="""
            {
                "implementation_timeline": {
                    "phase_1_design": {
                        "duration": "Weeks 1-4",
                        "activities": [
                            "CAD design of honeycomb panel geometry",
                            "Face sheet thickness optimization via FEA",
                            "Honeycomb core selection (cell size, density)",
                            "Bonding process specification",
                            "Edge sealing design"
                        ],
                        "deliverables": [
                            "Complete CAD model",
                            "FEA report with safety factors",
                            "Materials specifications",
                            "Process flow diagram"
                        ],
                        "resources": "2 mechanical engineers, 1 materials engineer, CAD/FEA software",
                        "cost": "$40k-60k (labor)",
                        "risks": ["Design iterations if FEA shows issues", "Mitigation: Conservative initial design"]
                    },
                    "phase_2_procurement": {
                        "duration": "Weeks 3-10 (parallel with design)",
                        "activities": [
                            "Supplier qualification (Hexcel, 3M, Kaiser)",
                            "Equipment procurement (vacuum bag, oven)",
                            "Tooling/fixture design and fabrication",
                            "Materials ordering"
                        ],
                        "deliverables": [
                            "Qualified supplier agreements",
                            "Equipment installed and commissioned",
                            "Tooling ready for use",
                            "Materials in stock"
                        ],
                        "resources": "1 procurement specialist, 1 manufacturing engineer",
                        "cost": "$80k-150k (equipment + tooling + materials)",
                        "risks": ["Supplier lead time delays", "Mitigation: Order long-lead items early"]
                    },
                    "phase_3_process_development": {
                        "duration": "Weeks 8-14",
                        "activities": [
                            "Bonding process trials (temperature, pressure, time)",
                            "Face sheet forming trials",
                            "Edge sealing method validation",
                            "Quality inspection procedures",
                            "Manufacturing work instructions"
                        ],
                        "deliverables": [
                            "Validated bonding process parameters",
                            "Process control plan",
                            "Work instructions",
                            "Quality inspection criteria"
                        ],
                        "resources": "1 process engineer, 2 technicians, materials for trials",
                        "cost": "$35k-50k (labor + trial materials)",
                        "risks": ["Bonding failures requiring rework", "Mitigation: Follow aerospace best practices"]
                    },
                    "phase_4_prototyping": {
                        "duration": "Weeks 12-18",
                        "activities": [
                            "Build 5 prototype panels",
                            "Dimensional inspection",
                            "Mechanical testing (bending, compression)",
                            "Environmental testing (temperature, humidity)",
                            "Design refinement based on test results"
                        ],
                        "deliverables": [
                            "5 prototype panels",
                            "Test reports (mechanical + environmental)",
                            "Design revision (if needed)",
                            "Prototype validation report"
                        ],
                        "resources": "2 engineers, 2 technicians, test equipment, test lab",
                        "cost": "$50k-80k (labor + testing + materials)",
                        "risks": ["Test failures requiring redesign", "Mitigation: Conservative design margins"]
                    },
                    "phase_5_validation": {
                        "duration": "Weeks 16-22",
                        "activities": [
                            "Build 10-20 pilot production units",
                            "Assembly into complete system",
                            "System-level testing",
                            "Customer validation (if applicable)",
                            "Manufacturing cost validation"
                        ],
                        "deliverables": [
                            "Pilot production units",
                            "System test results",
                            "Customer approval (if needed)",
                            "Validated cost model"
                        ],
                        "resources": "Full production team (scaled down)",
                        "cost": "$60k-100k (labor + materials)",
                        "risks": ["System integration issues", "Mitigation: Early system-level design review"]
                    },
                    "phase_6_production_ramp": {
                        "duration": "Weeks 20-30",
                        "activities": [
                            "Production training for operators",
                            "Ramp production volume 10 → 50 → 200 units",
                            "Process optimization for cycle time",
                            "Supply chain scaling",
                            "Quality system implementation"
                        ],
                        "deliverables": [
                            "Trained production team",
                            "Production at target rate",
                            "Optimized process (reduced cycle time)",
                            "Quality system operational"
                        ],
                        "resources": "Production team (4-8 operators), production manager",
                        "cost": "$80k-150k (labor + production materials)",
                        "risks": ["Yield issues during ramp", "Mitigation: Gradual volume increase with monitoring"]
                    }
                },
                "total_timeline": "30 weeks (7.5 months) from start to production",
                "total_cost": "$345k-590k (engineering + equipment + tooling + pilot production)",
                "critical_path": "Design → Procurement (long-lead) → Process Development → Prototyping → Validation → Ramp",
                "acceleration_opportunities": [
                    "Overlap design and procurement (save 2 weeks)",
                    "Use external test lab (save 1-2 weeks)",
                    "Fast-track supplier qualification (save 1 week)"
                ],
                "accelerated_timeline": "24-26 weeks possible with fast-tracking"
            }
            """,
            why_this_matters="Detailed timeline transforms TRIZ solution into executable project plan. Shows what needs to happen when, with what resources, and what risks to manage.",
            related_triz_tool="Implementation Planning - Project Management",
        )

    elif step_num == 60:
        return StepInstruction(
            task="Generate FINAL SYNTHESIS: Complete TRIZ solution with ALL evidence from 59 previous research steps",
            search_queries=[
                "TRIZ final report synthesis methodology",
                "comprehensive solution documentation",
                "evidence-based recommendation",
            ],
            extract_requirements=[
                "executive_summary",
                "triz_methodology_applied",
                "recommended_solution_details",
                "supporting_evidence",
                "implementation_roadmap",
                "future_triz_iterations",
            ],
            validation_criteria="Must synthesize ALL 59 steps into cohesive final solution with complete evidence chain",
            expected_output_format="""
            {
                "executive_summary": {
                    "problem": "Original problem statement from Step 1",
                    "current_ideality": "0.90 (from Step 9)",
                    "recommended_solution": "Honeycomb Aluminum Structure (from Step 57)",
                    "projected_ideality": "1.57 (+74% improvement)",
                    "key_benefits": ["40-50% weight reduction", "Maintains formability", "Proven technology", "Moderate cost increase"],
                    "implementation_timeline": "30 weeks to production",
                    "investment_required": "$345k-590k",
                    "confidence": "HIGH - proven aerospace technology with established suppliers"
                },
                "triz_methodology_applied": {
                    "phase_1_understand_scope": {
                        "tools_used": ["9 Boxes", "Ideality Audit"],
                        "key_findings": [
                            "Step 1-5: 9 Boxes revealed weight-formability as core contradiction across time/scale",
                            "Step 6-9: Current Ideality 0.90 (acceptable but far from ideal)",
                            "Step 10: Root cause identified - material choice drives contradiction"
                        ],
                        "evidence": "Steps 1-10 accumulated knowledge"
                    },
                    "phase_2_define_ideal": {
                        "tools_used": ["Ideal Outcome", "Resources"],
                        "key_findings": [
                            "Step 11: Ideal = 50% lighter + easy forming + low cost",
                            "Step 13: Resources available: gravity, ambient air, existing tooling",
                            "Step 16: Ideal Ideality target = 2.0+"
                        ],
                        "evidence": "Steps 11-16 accumulated knowledge"
                    },
                    "phase_3_function_analysis": {
                        "tools_used": ["Function Map", "Contradictions"],
                        "key_findings": [
                            "Step 17-21: Function Map identified 'aluminum adds weight' as primary harmful function",
                            "Step 23: Technical Contradiction confirmed - reducing weight worsens formability",
                            "Step 24: Physical Contradiction - need flexible (for forming) AND rigid (for structure)"
                        ],
                        "evidence": "Steps 17-26 accumulated knowledge"
                    },
                    "phase_4_select_tools": {
                        "tools_used": ["Contradiction Matrix", "Standard Solutions", "Effects Database"],
                        "key_findings": [
                            "Step 28-29: Mapped to Parameters 1 (Weight) vs 32 (Ease of manufacture), Matrix recommended Principles 1, 40, 15, 35",
                            "Step 30: Standard Solution - Eliminate harm via material substitution",
                            "Step 31: Effects Database found induction heating for warm forming"
                        ],
                        "evidence": "Steps 27-32 accumulated knowledge"
                    },
                    "phase_5_generate_solutions": {
                        "tools_used": ["40 Principles", "Standard Solutions", "Materials Database", "Effects"],
                        "key_findings": [
                            "Step 33-36: Principle 1 (Segmentation) applied → modular design + honeycomb structure",
                            "Step 37-40: Principle 40 (Composites) applied → multi-material + honeycomb core",
                            "Step 42-45: Standard Solutions generated harm elimination strategies",
                            "Step 47-49: DEEP materials research identified magnesium (34% lighter), CFRP (42% lighter), honeycomb (40-50% lighter)",
                            "Step 50: Synthesized 3 complete solutions combining multiple TRIZ tools"
                        ],
                        "evidence": "Steps 33-50 accumulated knowledge with 44+ materials books"
                    },
                    "phase_6_rank_implement": {
                        "tools_used": ["Ideality Equation", "Ideality Plot", "Implementation Planning"],
                        "key_findings": [
                            "Step 51-54: Calculated Ideality for all solutions - Honeycomb Aluminum scored 1.57",
                            "Step 55-56: Ideality Plot positioned Honeycomb in Q1 (Implement Now)",
                            "Step 57: Selected Honeycomb as primary + Magnesium as R&D track",
                            "Step 58-59: Validated implementation with suppliers, costs, timeline"
                        ],
                        "evidence": "Steps 51-59 accumulated knowledge"
                    }
                },
                "recommended_solution_details": {
                    "solution": "Aluminum Honeycomb Core Structure with Thin Face Sheets",
                    "how_it_works": "Replace solid aluminum sheet with honeycomb core (hexagonal cells) sandwiched between thin aluminum face sheets, bonded with aerospace adhesive",
                    "triz_principles_applied": [
                        "Principle 1 (Segmentation - fragmentation variant): Segment solid material into cellular structure",
                        "Principle 3 (Local Quality): Solid face sheets where needed, hollow core inside",
                        "Standard Solution (Eliminate Harm): Remove 50% of aluminum mass while maintaining strength",
                        "Materials Selection: Keep aluminum for formability, optimize structure for weight"
                    ],
                    "benefits_achieved": [
                        "40-50% weight reduction (from 2.70 to ~1.4-1.6 effective density)",
                        "Maintains aluminum formability (face sheets bend normally)",
                        "Better energy absorption than solid (honeycomb crushes progressively)",
                        "Proven aerospace technology reduces risk",
                        "Established suppliers (Hexcel, Plascore) available"
                    ],
                    "costs_incurred": [
                        "Material cost: $150-300 per panel (vs $80-120 solid aluminum)",
                        "Equipment: $40k-120k capital (vacuum bag, oven, tooling)",
                        "Labor: More complex assembly, bonding process",
                        "Lead time: Honeycomb procurement 4-6 weeks"
                    ],
                    "harms_minimized": [
                        "Weight harm reduced 40-50% (primary goal)",
                        "Manufacturing complexity moderate (aerospace-proven processes)",
                        "Cost increase justified by weight savings value"
                    ],
                    "ideality_improvement": {
                        "current": 0.90,
                        "projected": 1.57,
                        "improvement": "+74%",
                        "calculation": "Benefits +30%, Costs +15%, Harms -40% → Net Ideality +74%"
                    }
                },
                "supporting_evidence": {
                    "9_boxes_analysis": "Steps 1-5 data",
                    "ideality_audit": "Steps 6-9 data",
                    "function_map": "Steps 17-21 data",
                    "contradictions": "Steps 23-24 data",
                    "contradiction_matrix": "Steps 28-29 data",
                    "materials_research": "Steps 47-49 data from 44+ engineering books",
                    "supplier_validation": "Step 58 data",
                    "timeline_validation": "Step 59 data"
                },
                "implementation_roadmap": {
                    "immediate_actions": [
                        "Week 1: Engage Hexcel for honeycomb core samples and technical consultation",
                        "Week 1: Begin CAD design of panel geometry",
                        "Week 2: FEA analysis to optimize face sheet thickness and core density",
                        "Week 3: Order long-lead equipment (vacuum bagging, oven if needed)"
                    ],
                    "30_week_plan": "See Step 59 detailed timeline",
                    "success_criteria": [
                        "Achieve 40%+ weight reduction vs baseline aluminum",
                        "Pass mechanical testing (bending, compression) with 2x safety factor",
                        "Formability demonstrated (bend radius ≤ 2x solid aluminum)",
                        "Manufacturing cost ≤ 2x solid aluminum",
                        "Production rate ≥ 80% of target by Week 30"
                    ]
                },
                "future_triz_iterations": {
                    "next_generation_1": {
                        "focus": "Modular Magnesium Segments - highest Ideality potential (1.79)",
                        "triz_problems_to_solve": [
                            "Apply TRIZ to magnesium corrosion (use coating, anodizing)",
                            "Apply TRIZ to snap-fit reliability (segmentation + backup locking)",
                            "Apply TRIZ to warm forming process (induction heating integration)"
                        ],
                        "timeline": "12-18 months parallel R&D track",
                        "potential": "+99% Ideality improvement if successful"
                    },
                    "next_generation_2": {
                        "focus": "Evolution Trends - increasing dynamism",
                        "opportunity": "Apply Trend 'Increasing Dynamism' to create adaptive/morphing structure",
                        "triz_approach": "Research shape-memory alloys, smart materials, variable-geometry structures",
                        "timeline": "18-24 months advanced R&D"
                    },
                    "continuous_improvement": {
                        "focus": "Current honeycomb solution optimization",
                        "opportunities": [
                            "Optimize honeycomb cell size for weight-strength (smaller trials)",
                            "Reduce bonding cycle time (process optimization)",
                            "Trim excess material more efficiently (Trimming Standard Solution)"
                        ]
                    }
                },
                "conclusion": {
                    "summary": "Complete 60-step TRIZ methodology successfully identified Aluminum Honeycomb Structure as optimal solution, achieving 74% Ideality improvement with proven technology and manageable risk. Implementation validated with suppliers, costs, and timeline. Parallel R&D track on Modular Magnesium offers future 99% Ideality potential.",
                    "confidence": "HIGH - aerospace-proven technology, established suppliers, validated implementation path",
                    "recommendation": "PROCEED with Honeycomb Aluminum implementation immediately while initiating parallel TRIZ iteration on Modular Magnesium for next-generation solution.",
                    "triz_value_delivered": "TRIZ methodology provided: (1) Systematic problem understanding via 9 Boxes, (2) Quantified current state via Ideality, (3) Identified contradictions as core problem, (4) Applied proven principles from patent analysis, (5) Generated multiple solutions, (6) Ranked by Ideality, (7) Validated implementation feasibility. Total research depth: 60 steps, 44+ engineering books, complete evidence chain."
                }
            }
            """,
            why_this_matters="This final synthesis is the DELIVERABLE of complete TRIZ methodology. It demonstrates the full journey from problem to solution with complete evidence, quantified Ideality improvement, and validated implementation path. This is what makes TRIZ valuable - systematic, evidence-based innovation.",
            related_triz_tool="Complete TRIZ Methodology - Final Synthesis",
        )

    else:
        raise ValueError(f"Invalid step number {step_num} for Phase 6 (valid: 51-60)")
