"""
Handler for Complete TRIZ Solver
Formats the comprehensive 8-phase analysis for Claude
"""

from typing import Dict, Any
from triz_tools.models import TRIZToolResponse


def handle_solve_complete(problem: str) -> TRIZToolResponse:
    """
    Execute complete TRIZ analysis and format for Claude.

    Args:
        problem: Detailed problem description

    Returns:
        Formatted markdown response with all 8 phases
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from triz_tools.complete_triz_solver import solve_with_complete_triz

    # Run complete TRIZ analysis
    result = solve_with_complete_triz(problem)

    # Format comprehensive response
    output = []
    output.append("# 🎯 COMPLETE TRIZ ANALYSIS")
    output.append(
        f"\n**Problem:** {problem[:200]}...\n"
        if len(problem) > 200
        else f"\n**Problem:** {problem}\n"
    )
    output.append(f"**Phases Completed:** {len(result['phases_completed'])}/8\n")
    output.append("---\n")

    # PHASE 1: Function Analysis
    output.append("## 📋 PHASE 1: Function Analysis\n")
    fa = result.get("function_analysis")
    if fa:
        output.append(f"**Main Function:** {fa.main_function}\n")
        if fa.auxiliary_functions:
            output.append(f"**Auxiliary Functions:**")
            for func in fa.auxiliary_functions:
                output.append(f"- {func}")
        if fa.harmful_functions:
            output.append(f"\n**Harmful Functions:**")
            for func in fa.harmful_functions:
                output.append(f"- {func}")
        output.append("")

    # PHASE 2: Resource Inventory
    output.append("## 🔍 PHASE 2: Resource Inventory\n")
    res = result.get("resource_inventory")
    if res:
        if res.substance_resources:
            output.append(
                f"**Substance Resources:** {', '.join(res.substance_resources[:4])}"
            )
        if res.field_resources:
            output.append(f"**Field Resources:** {', '.join(res.field_resources)}")
        output.append("")

    # PHASE 3: Ideal Final Result
    output.append("## ⭐ PHASE 3: Ideal Final Result\n")
    ifr = result.get("ideal_final_result", {})
    if ifr:
        output.append(f"**IFR:** {ifr.get('ifr_statement', 'N/A')}\n")
        if ifr.get("x_element"):
            output.append(f"**X-Element Insight:** {ifr['x_element']}\n")

    # PHASE 4: Contradictions (KEY INSIGHT!)
    output.append("## ⚡ PHASE 4: Contradiction Analysis\n")

    tech_contras = result.get("technical_contradictions", [])
    if tech_contras:
        output.append("### Technical Contradictions\n")
        for i, tc in enumerate(tech_contras, 1):
            output.append(f"**{i}. {tc.description}**")
            output.append(f"- Improving: {tc.improving_parameter}")
            output.append(f"- Worsening: {tc.worsening_parameter}")
            output.append(f"- Recommended Principles: {tc.recommended_principles}\n")

    phys_contras = result.get("physical_contradictions", [])
    if phys_contras:
        output.append("### Physical Contradictions (Opposite Requirements!)\n")
        for i, pc in enumerate(phys_contras, 1):
            output.append(f"**{i}. {pc.parameter}**")
            output.append(f"- Must be: {pc.requirement_1}")
            output.append(f"- Must be: {pc.requirement_2}")
            output.append(f"\n**Separation Methods:**")
            for method in pc.separation_methods:
                output.append(f"  - {method}")
            output.append("")

    # PHASE 5: Multi-Method Solutions
    output.append("## 🎯 PHASE 5: Solution Methods\n")

    princ_sols = result.get("principle_based_solutions", [])
    if princ_sols:
        output.append(f"### Inventive Principles ({len(princ_sols)} identified)\n")
        for i, sol in enumerate(princ_sols[:3], 1):
            output.append(
                f"**{i}. Principle {sol['principle_number']}: {sol['principle_name']}**"
            )
            output.append(f"{sol['description'][:150]}...")
            if sol.get("sub_principles"):
                output.append(
                    f"*Sub-principles:* {', '.join(sol['sub_principles'][:2])}"
                )
            output.append("")

    sep_sols = result.get("separation_solutions", [])
    if sep_sols:
        output.append(f"### Separation Principles ({len(sep_sols)} solutions)\n")
        for i, sol in enumerate(sep_sols[:2], 1):
            output.append(f"**{i}. {sol['separation_method']}**")
            output.append(f"{sol['example_application']}\n")

    # PHASE 6: Materials Analysis (if present)
    if result.get("materials_analysis"):
        output.append("## 🔬 PHASE 6: Materials Analysis\n")
        ma = result["materials_analysis"]

        if ma.get("materials_identified"):
            output.append(
                f"**Materials Identified:** {', '.join(ma['materials_identified'])}\n"
            )

        if ma.get("comparison_table"):
            output.append("**Material Comparison:**\n")
            output.append("| Material | Density | Weight vs Aluminum | Source |")
            output.append("|----------|---------|-------------------|--------|")
            for row in ma["comparison_table"]:
                output.append(
                    f"| {row['material']} | {row['density']} g/cm³ | {row['weight_vs_aluminum']} | {row['source'][:30]}... |"
                )
            output.append("")

    # PHASE 7: Final Solutions
    output.append("## 🏆 PHASE 7: Synthesized Solutions\n")
    final_sols = result.get("final_solutions", [])
    if final_sols:
        for i, sol in enumerate(final_sols[:5], 1):
            output.append(f"### Solution {i}: {sol['title']}\n")
            output.append(f"**TRIZ Method:** {sol['triz_method']}")
            output.append(f"**Feasibility:** {sol['feasibility']:.1%}")
            output.append(
                f"**Innovation Level:** {sol.get('innovation_level', 'N/A')}/5"
            )
            if sol.get("specific_materials"):
                output.append(
                    f"**Specific Materials:** {', '.join(sol['specific_materials'])}"
                )
            output.append(f"\n{sol.get('description', '')[:200]}...\n")

    # PHASE 8: Implementation
    if result.get("implementation_guide"):
        output.append("## 🛠️ PHASE 8: Implementation Guide\n")
        impl = result["implementation_guide"]
        output.append(f"**Timeline:** {impl.get('timeline', 'TBD')}\n")
        output.append("**Steps:**")
        for step in impl.get("steps", []):
            output.append(f"{step}")
        output.append("")

    output.append("---")
    output.append(
        f"\n✅ **Complete TRIZ analysis finished:** {len(result['phases_completed'])} phases executed\n"
    )

    formatted_output = "\n".join(output)

    # Return TRIZToolResponse object
    return TRIZToolResponse(
        success=True,
        message=f"Complete TRIZ analysis finished: {len(result['phases_completed'])} phases executed",
        data={
            "formatted_report": formatted_output,
            "phases_completed": result["phases_completed"],
            "problem": problem,
        },
    )
