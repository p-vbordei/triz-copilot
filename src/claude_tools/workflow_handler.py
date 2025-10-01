"""
Workflow Handlers (TASK-013, TASK-014, TASK-015)
Handle guided TRIZ workflow commands for Claude
"""

from typing import Dict, Any
from triz_tools import workflow_tools
from triz_tools.models import TRIZToolResponse


def handle_workflow_start() -> TRIZToolResponse:
    """
    Handle workflow start command

    Returns:
        TRIZToolResponse with session information
    """
    return workflow_tools.triz_workflow_start()


def handle_workflow_continue(session_id: str, user_input: str) -> TRIZToolResponse:
    """
    Handle workflow continue command

    Args:
        session_id: Active session identifier
        user_input: User's response to current stage

    Returns:
        TRIZToolResponse with next stage information
    """
    return workflow_tools.triz_workflow_continue(session_id, user_input)


def handle_workflow_reset(session_id: str) -> TRIZToolResponse:
    """
    Reset a workflow session to the beginning

    Args:
        session_id: Session to reset

    Returns:
        TRIZToolResponse with confirmation
    """
    try:
        # Get session and reset to initial stage
        from triz_tools.session_manager import SessionManager
        manager = SessionManager()
        session = manager.get_session(session_id)

        if not session:
            return TRIZToolResponse(
                success=False,
                message=f"Session not found: {session_id}",
                data={}
            )

        # Reset session
        from triz_tools.models import WorkflowStage
        session.current_stage = WorkflowStage.PROBLEM_DEFINITION
        session.session_data.problem_statement = ""
        session.session_data.ideal_final_result = ""
        session.session_data.contradictions = []
        session.session_data.selected_principles = []
        session.session_data.solutions = []

        manager.save_session(session)

        return TRIZToolResponse(
            success=True,
            message="Workflow session reset to beginning",
            data={
                "session_id": session_id,
                "stage": WorkflowStage.PROBLEM_DEFINITION.value
            },
            session_id=session_id,
            stage=WorkflowStage.PROBLEM_DEFINITION
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to reset session: {str(e)}",
            data={}
        )


def handle_workflow_status(session_id: str) -> TRIZToolResponse:
    """
    Get the current status of a workflow session

    Args:
        session_id: Session identifier

    Returns:
        TRIZToolResponse with session status
    """
    try:
        from triz_tools.session_manager import SessionManager
        manager = SessionManager()
        session = manager.get_session(session_id)

        if not session:
            return TRIZToolResponse(
                success=False,
                message=f"Session not found: {session_id}",
                data={}
            )

        # Build status data
        status_data = {
            "session_id": session_id,
            "current_stage": session.current_stage.value,
            "workflow_type": session.workflow_type.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "interactions_count": len(session.interactions),
            "has_problem_statement": bool(session.session_data.problem_statement),
            "has_ifr": bool(session.session_data.ideal_final_result),
            "contradictions_count": len(session.session_data.contradictions),
            "principles_count": len(session.session_data.selected_principles),
            "solutions_count": len(session.session_data.solutions),
        }

        return TRIZToolResponse(
            success=True,
            message="Session status retrieved",
            data=status_data,
            session_id=session_id,
            stage=session.current_stage
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to get session status: {str(e)}",
            data={}
        )
