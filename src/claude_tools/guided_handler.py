"""
MCP Handler for Guided TRIZ Research
Handles triz_research_start and triz_research_submit tools

This handler manages the 60-step guided TRIZ methodology where
the AI performs iterative research through all 6 phases of TRIZ.
"""

from typing import Dict, Any
from src.triz_tools.models import TRIZToolResponse
from src.triz_tools.guided_triz_solver import (
    start_guided_triz_research,
    submit_research_findings,
)


def handle_research_start(problem: str) -> TRIZToolResponse:
    """
    Start guided TRIZ research session

    Args:
        problem: Problem description

    Returns:
        TRIZToolResponse with session_id and first step instructions
    """
    try:
        result = start_guided_triz_research(problem)

        formatted_instruction = _format_research_start(result)

        return TRIZToolResponse(
            success=True,
            message=f"TRIZ research session started: {result['session_id']}",
            data={
                "formatted_output": formatted_instruction,
                "session_id": result["session_id"],
                "current_step": result["current_step"],
                "instruction": result["instruction"],
            },
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False, message=f"Failed to start TRIZ research: {str(e)}", data={}
        )


def handle_research_submit(
    session_id: str, findings: Dict[str, Any]
) -> TRIZToolResponse:
    """
    Submit research findings and get next step

    Args:
        session_id: Session ID from start
        findings: Research findings dictionary

    Returns:
        TRIZToolResponse with validation and next step (or final solution)
    """
    try:
        result = submit_research_findings(session_id, findings)

        if not result["success"]:
            # Validation failed
            formatted_error = _format_validation_error(result)
            return TRIZToolResponse(
                success=False,
                message=result["error"],
                data={
                    "formatted_output": formatted_error,
                    "hint": result.get("hint", ""),
                    "instruction": result.get("instruction", {}),
                    "progress": result.get("progress", ""),
                },
            )

        if result.get("completed"):
            # Final step completed
            formatted_output = _format_completion(result)

            return TRIZToolResponse(
                success=True,
                message="TRIZ research completed successfully",
                data={
                    "formatted_output": formatted_output,
                    "final_solution": result["final_solution"],
                    "session_summary": result["session_summary"],
                },
            )

        # Next step
        formatted_instruction = _format_next_step(result)

        return TRIZToolResponse(
            success=True,
            message=f"Step {result['step_completed']} completed. Moving to step {result['current_step']}",
            data={
                "formatted_output": formatted_instruction,
                "current_step": result["current_step"],
                "progress": result["progress"],
                "instruction": result["instruction"],
            },
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to submit research: {str(e)}",
            data={"error_details": str(e)},
        )


def _format_research_start(result: Dict[str, Any]) -> str:
    """Format research start instruction for display"""
    instruction = result["instruction"]
    context = result["context"]

    return f"""# 🚀 TRIZ GUIDED RESEARCH SESSION STARTED

**Session ID:** `{result["session_id"]}`
**Total Steps:** {result["total_steps"]}
**Current Step:** {result["current_step"]}/60
**Phase:** {result["phase"]} - {result["phase_description"]}

---

## 📋 YOUR RESEARCH TASK (Step {result["current_step"]}):

**{instruction["task"]}**

### 🔍 Search These in Knowledge Base:

{chr(10).join(f"{i + 1}. {q}" for i, q in enumerate(instruction["search_queries"]))}

### 📊 Extract These from Research:

{chr(10).join(f"- **{r}**" for r in instruction["extract"])}

### ✅ Validation Criteria:

{instruction["validation"]}

### 📝 Expected Output Format:

```json
{instruction["format"]}
```

### 💡 Why This Matters:

{instruction["why"]}

### 🎯 TRIZ Tool:

**{instruction.get("related_triz_tool", "N/A")}**

---

**Progress:** {context["progress"]}
**Phase Progress:** {context["phase_progress"]}

**IMPORTANT:** Submit your findings using `triz_research_submit` with session_id="{result["session_id"]}" and findings dictionary matching the extract requirements above.
"""


def _format_next_step(result: Dict[str, Any]) -> str:
    """Format next step instruction for display"""
    instruction = result["instruction"]

    return f"""# ✅ Step {result["step_completed"]} Validated!

**Validation:** {result["validation"]}

---

## 📋 NEXT RESEARCH TASK (Step {result["current_step"]}/60):

**Phase:** {result["phase"]} - {result["phase_description"]}
**Progress:** {result["progress"]}
**Phase Progress:** {result.get("phase_progress", "N/A")}

---

**{instruction["task"]}**

### 🔍 Search These:

{chr(10).join(f"{i + 1}. {q}" for i, q in enumerate(instruction["search_queries"]))}

### 📊 Extract These:

{chr(10).join(f"- **{r}**" for r in instruction["extract"])}

### ✅ Validation:

{instruction["validation"]}

### 📝 Format:

```json
{instruction["format"]}
```

### 💡 Why:

{instruction["why"]}

### 🎯 TRIZ Tool:

**{instruction.get("related_triz_tool", "N/A")}**

---

**CONTINUE:** Submit findings using `triz_research_submit` with same session_id.
"""


def _format_validation_error(result: Dict[str, Any]) -> str:
    """Format validation error for display"""
    instruction = result.get("instruction", {})

    error_msg = f"""# ❌ Step {result["current_step"]} Validation Failed

**Error:** {result["error"]}

**Hint:** {result.get("hint", "Review the extract requirements carefully.")}

---

## 🔄 RETRY: Same Research Task (Step {result["current_step"]}):

**{instruction.get("task", "Complete the research task")}**

### Required Findings:

{chr(10).join(f"- **{r}**" for r in instruction.get("extract", []))}

### What to Search:

{chr(10).join(f"{i + 1}. {q}" for i, q in enumerate(instruction.get("search_queries", [])))}

---

**Progress:** {result["progress"]}

**ACTION:** Fix the missing/incomplete findings and resubmit using `triz_research_submit`.
"""

    return error_msg


def _format_completion(result: Dict[str, Any]) -> str:
    """Format final completion message"""
    final_solution = result.get("final_solution", {})
    session_summary = result.get("session_summary", {})
    triz_artifacts = result.get("triz_artifacts", {})

    exec_summary = final_solution.get("executive_summary", {})
    recommended = final_solution.get("recommended_solution", {})

    return f"""# ✅ TRIZ RESEARCH COMPLETED!

**Total Steps Completed:** {result["total_steps"]}
**Methodology:** {final_solution.get("methodology", "Complete TRIZ 60-Step")}

---

## 🎯 EXECUTIVE SUMMARY

**Problem:** {exec_summary.get("problem", "See session data")}

**Current Ideality:** {exec_summary.get("current_ideality", "N/A")}
**Projected Ideality:** {exec_summary.get("projected_ideality", "N/A")}
**Improvement:** {exec_summary.get("improvement", "N/A")}

**Recommended Solution:** {exec_summary.get("recommended_solution", "See details below")}

### Key Benefits:
{chr(10).join(f"- {b}" for b in exec_summary.get("key_benefits", []))}

**Implementation Timeline:** {exec_summary.get("implementation_timeline", "See roadmap")}
**Investment Required:** {exec_summary.get("investment_required", "See details")}
**Confidence:** {exec_summary.get("confidence", "N/A")}

---

## 📊 TRIZ METHODOLOGY APPLIED

### Phase 1: Understand & Scope (Steps 1-10)
**Tools:** 9 Boxes + Ideality Audit
**Completed:** {session_summary.get("phases_summary", {}).get("phase_1_understand_scope", {}).get("completed", 0)}/10 steps

### Phase 2: Define Ideal (Steps 11-16)
**Tools:** Ideal Outcome + Resources
**Completed:** {session_summary.get("phases_summary", {}).get("phase_2_define_ideal", {}).get("completed", 0)}/6 steps

### Phase 3: Function Analysis (Steps 17-26)
**Tools:** Function Map + Contradictions
**Completed:** {session_summary.get("phases_summary", {}).get("phase_3_function_analysis", {}).get("completed", 0)}/10 steps

### Phase 4: Select Tools (Steps 27-32)
**Tools:** Contradiction Matrix + Tool Selection
**Completed:** {session_summary.get("phases_summary", {}).get("phase_4_select_tools", {}).get("completed", 0)}/6 steps

### Phase 5: Generate Solutions (Steps 33-50)
**Tools:** 40 Principles + Standard Solutions + Effects + Materials
**Completed:** {session_summary.get("phases_summary", {}).get("phase_5_generate_solutions", {}).get("completed", 0)}/18 steps

### Phase 6: Rank & Implement (Steps 51-60)
**Tools:** Ideality Plot + Implementation Planning
**Completed:** {session_summary.get("phases_summary", {}).get("phase_6_rank_implement", {}).get("completed", 0)}/10 steps

---

## 🔬 RECOMMENDED SOLUTION DETAILS

{_format_solution_details(recommended)}

---

## 🔬 TRIZ ARTIFACTS

**9 Boxes Analysis:** {_summarize_dict(triz_artifacts.get("nine_boxes", {}))}

**Current Ideality:** {_summarize_dict(triz_artifacts.get("current_ideality", {}))}

**Ideal Outcome:** {_summarize_dict(triz_artifacts.get("ideal_outcome", {}))}

**Function Map:** {_summarize_dict(triz_artifacts.get("function_map", {}))}

**Technical Contradictions:** {len(triz_artifacts.get("contradictions", {}).get("technical", []))} identified

**Physical Contradictions:** {len(triz_artifacts.get("contradictions", {}).get("physical", []))} identified

**Solution Concepts:** {len(triz_artifacts.get("solutions", []))} generated

---

## 🚀 IMPLEMENTATION ROADMAP

{_format_implementation_roadmap(final_solution.get("implementation_roadmap", {}))}

---

## 🔮 FUTURE TRIZ ITERATIONS

{_format_future_iterations(final_solution.get("future_iterations", {}))}

---

## 📝 CONCLUSION

{final_solution.get("conclusion", {}).get("summary", "TRIZ methodology completed successfully.")}

**Recommendation:** {final_solution.get("conclusion", {}).get("recommendation", "Review solution details above.")}

**Session ID:** {session_summary.get("session_id", "N/A")}
**Duration:** {session_summary.get("duration", "See timestamps")}

---

✨ **TRIZ 60-Step Guided Research Complete** ✨
"""


def _format_solution_details(solution: Dict[str, Any]) -> str:
    """Format solution details section"""
    if not solution:
        return "See final synthesis in step 60 accumulated knowledge."

    details = f"""**Solution:** {solution.get("solution", "N/A")}

**How It Works:** {solution.get("how_it_works", "N/A")}

**TRIZ Principles Applied:**
{chr(10).join(f"- {p}" for p in solution.get("triz_principles_applied", []))}

**Benefits:**
{chr(10).join(f"- {b}" for b in solution.get("benefits_achieved", []))}

**Costs:**
{chr(10).join(f"- {c}" for c in solution.get("costs_incurred", []))}

**Ideality Improvement:**
- Current: {solution.get("ideality_improvement", {}).get("current", "N/A")}
- Projected: {solution.get("ideality_improvement", {}).get("projected", "N/A")}
- Improvement: {solution.get("ideality_improvement", {}).get("improvement", "N/A")}
"""
    return details


def _format_implementation_roadmap(roadmap: Dict[str, Any]) -> str:
    """Format implementation roadmap"""
    if not roadmap:
        return "See step 59 for detailed implementation timeline."

    immediate = roadmap.get("immediate_actions", [])
    if immediate:
        return f"""**Immediate Actions:**
{chr(10).join(f"- {action}" for action in immediate)}

**Full Timeline:** {roadmap.get("full_timeline", "See step 59 accumulated knowledge")}

**Success Criteria:**
{chr(10).join(f"- {criteria}" for criteria in roadmap.get("success_criteria", []))}
"""
    return "See step 59 for complete implementation plan."


def _format_future_iterations(iterations: Dict[str, Any]) -> str:
    """Format future TRIZ iterations"""
    if not iterations:
        return "See step 60 for future iteration recommendations."

    next_gen = iterations.get("next_generation_1", {})
    if next_gen:
        return f"""**Next Generation Focus:** {next_gen.get("focus", "N/A")}

**TRIZ Problems to Solve:**
{chr(10).join(f"- {problem}" for problem in next_gen.get("triz_problems_to_solve", []))}

**Timeline:** {next_gen.get("timeline", "N/A")}
**Potential:** {next_gen.get("potential", "N/A")}
"""
    return "See step 60 for future iteration opportunities."


def _summarize_dict(data: Dict[str, Any]) -> str:
    """Summarize dictionary for display"""
    if not data:
        return "Not available"

    # Return count or brief summary
    if isinstance(data, dict):
        return f"{len(data)} items"
    return str(data)[:100]
