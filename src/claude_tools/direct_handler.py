"""
Direct Tool Handlers (TASK-021, TASK-022, TASK-023)
Handle direct TRIZ tool access for Claude
"""

from typing import Dict, Any
from triz_tools import direct_tools
from triz_tools.models import TRIZToolResponse


def handle_get_principle(principle_number: int) -> TRIZToolResponse:
    """
    Handle get principle command (TASK-021)

    Args:
        principle_number: TRIZ principle number (1-40)

    Returns:
        TRIZToolResponse with principle details
    """
    # Validate range
    if not isinstance(principle_number, int) or not 1 <= principle_number <= 40:
        return TRIZToolResponse(
            success=False,
            message=f"Invalid principle number: {principle_number}. Must be between 1 and 40.",
            data={"valid_range": "1-40"}
        )

    # Use existing direct tool
    return direct_tools.triz_tool_get_principle(principle_number)


def handle_contradiction_matrix(
    improving_parameter: int,
    worsening_parameter: int
) -> TRIZToolResponse:
    """
    Handle contradiction matrix lookup (TASK-022)

    Args:
        improving_parameter: Parameter to improve (1-39)
        worsening_parameter: Parameter that worsens (1-39)

    Returns:
        TRIZToolResponse with recommended principles
    """
    # Validate parameters
    errors = []
    if not isinstance(improving_parameter, int) or not 1 <= improving_parameter <= 39:
        errors.append(f"Improving parameter must be between 1 and 39, got {improving_parameter}")

    if not isinstance(worsening_parameter, int) or not 1 <= worsening_parameter <= 39:
        errors.append(f"Worsening parameter must be between 1 and 39, got {worsening_parameter}")

    if errors:
        return TRIZToolResponse(
            success=False,
            message="; ".join(errors),
            data={"valid_range": "1-39"}
        )

    # Use existing direct tool
    return direct_tools.triz_tool_contradiction_matrix(
        improving_parameter,
        worsening_parameter
    )


def handle_brainstorm(principle_number: int, context: str) -> TRIZToolResponse:
    """
    Handle brainstorm command (TASK-023)

    Args:
        principle_number: TRIZ principle number (1-40)
        context: Problem context for generating ideas

    Returns:
        TRIZToolResponse with generated ideas
    """
    # Validate principle number
    if not isinstance(principle_number, int) or not 1 <= principle_number <= 40:
        return TRIZToolResponse(
            success=False,
            message=f"Invalid principle number: {principle_number}. Must be between 1 and 40.",
            data={"valid_range": "1-40"}
        )

    # Validate context
    if not context or len(context.strip()) < 10:
        return TRIZToolResponse(
            success=False,
            message="Context too short. Please provide more details about your problem.",
            data={}
        )

    # Use existing direct tool
    return direct_tools.triz_tool_brainstorm(principle_number, context)


def handle_search_principles(query: str, top_k: int = 5) -> TRIZToolResponse:
    """
    Search for relevant principles using semantic search

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        TRIZToolResponse with matching principles
    """
    try:
        from triz_tools.services.vector_service import VectorService

        service = VectorService()
        results = service.search_principles(query, top_k=top_k)

        return TRIZToolResponse(
            success=True,
            message=f"Found {len(results)} relevant principle(s)",
            data={
                "query": query,
                "principles": results,
                "count": len(results)
            }
        )

    except Exception as e:
        # Fallback to file-based search
        try:
            from triz_tools.services.file_vector_service import FileVectorService

            service = FileVectorService()
            results = service.search_principles(query, top_k=top_k)

            return TRIZToolResponse(
                success=True,
                message=f"Found {len(results)} relevant principle(s) (file-based)",
                data={
                    "query": query,
                    "principles": results,
                    "count": len(results)
                }
            )
        except Exception as fallback_error:
            return TRIZToolResponse(
                success=False,
                message=f"Search failed: {str(e)}; Fallback failed: {str(fallback_error)}",
                data={}
            )


def handle_list_parameters() -> TRIZToolResponse:
    """
    List all 39 TRIZ engineering parameters

    Returns:
        TRIZToolResponse with parameter list
    """
    try:
        from triz_tools.contradiction_matrix import get_all_parameters

        parameters = get_all_parameters()

        return TRIZToolResponse(
            success=True,
            message="Retrieved all 39 TRIZ engineering parameters",
            data={
                "parameters": parameters,
                "count": len(parameters)
            }
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to retrieve parameters: {str(e)}",
            data={}
        )
