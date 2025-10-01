"""
Solve Handlers (TASK-017, TASK-018, TASK-019, TASK-020)
Handle autonomous TRIZ problem-solving for Claude
"""

from typing import Dict, Any, List
from triz_tools import solve_tools
from triz_tools.models import TRIZToolResponse


def handle_solve(problem: str) -> TRIZToolResponse:
    """
    Handle autonomous solve command

    Args:
        problem: Problem description (up to 2000 characters)

    Returns:
        TRIZToolResponse with complete analysis
    """
    # Validate problem length
    if len(problem) > 2000:
        return TRIZToolResponse(
            success=False,
            message="Problem description exceeds 2000 character limit",
            data={"max_length": 2000, "actual_length": len(problem)}
        )

    if len(problem.strip()) < 10:
        return TRIZToolResponse(
            success=False,
            message="Problem description too short. Please provide more details.",
            data={}
        )

    # Use existing autonomous solve tool
    return solve_tools.triz_solve_autonomous(problem)


def identify_contradictions(problem: str) -> TRIZToolResponse:
    """
    Identify technical and physical contradictions in a problem (TASK-018)

    Args:
        problem: Problem description

    Returns:
        TRIZToolResponse with identified contradictions
    """
    try:
        from triz_tools.services.analysis_service import AnalysisService

        service = AnalysisService()
        contradictions = service.identify_contradictions(problem)

        return TRIZToolResponse(
            success=True,
            message=f"Identified {len(contradictions)} contradiction(s)",
            data={
                "problem": problem,
                "contradictions": contradictions,
                "technical_count": len([c for c in contradictions if c.get("type") == "technical"]),
                "physical_count": len([c for c in contradictions if c.get("type") == "physical"]),
            }
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to identify contradictions: {str(e)}",
            data={}
        )


def recommend_principles(problem: str, top_k: int = 5) -> TRIZToolResponse:
    """
    Recommend TRIZ principles for a problem (TASK-019)

    Args:
        problem: Problem description
        top_k: Number of principles to recommend

    Returns:
        TRIZToolResponse with recommended principles
    """
    try:
        from triz_tools.services.vector_service import VectorService

        service = VectorService()
        principles = service.search_principles(problem, top_k=top_k)

        if not principles:
            return TRIZToolResponse(
                success=False,
                message="No relevant principles found",
                data={}
            )

        return TRIZToolResponse(
            success=True,
            message=f"Found {len(principles)} relevant principle(s)",
            data={
                "problem": problem,
                "recommended_principles": principles,
                "count": len(principles)
            }
        )

    except Exception as e:
        # Fallback to file-based search
        try:
            from triz_tools.services.file_vector_service import FileVectorService

            service = FileVectorService()
            principles = service.search_principles(problem, top_k=top_k)

            return TRIZToolResponse(
                success=True,
                message=f"Found {len(principles)} relevant principle(s) (file-based)",
                data={
                    "problem": problem,
                    "recommended_principles": principles,
                    "count": len(principles)
                }
            )
        except Exception as fallback_error:
            return TRIZToolResponse(
                success=False,
                message=f"Failed to recommend principles: {str(e)}; Fallback failed: {str(fallback_error)}",
                data={}
            )


def generate_solutions(
    problem: str,
    principles: List[Dict[str, Any]],
    count: int = 3
) -> TRIZToolResponse:
    """
    Generate solution concepts using TRIZ principles (TASK-020)

    Args:
        problem: Problem description
        principles: List of applicable principles
        count: Number of solutions to generate

    Returns:
        TRIZToolResponse with solution concepts
    """
    try:
        from triz_tools.services.analysis_service import AnalysisService

        service = AnalysisService()
        solutions = service.generate_solutions(problem, principles, count)

        return TRIZToolResponse(
            success=True,
            message=f"Generated {len(solutions)} solution concept(s)",
            data={
                "problem": problem,
                "solutions": solutions,
                "principles_used": [p.get("number") for p in principles],
                "count": len(solutions)
            }
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to generate solutions: {str(e)}",
            data={}
        )
