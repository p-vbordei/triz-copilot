"""
TRIZ Workflow Tools (T037)
Implementation of guided workflow functions
"""

from typing import Dict, Any, Optional
from pathlib import Path
import uuid

from .models import (
    TRIZToolResponse,
    ProblemSession,
    WorkflowStage,
    WorkflowType,
)


# Session storage directory
SESSIONS_DIR = Path.home() / ".triz_sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

# Active sessions cache
_active_sessions: Dict[str, ProblemSession] = {}


def triz_workflow_start() -> TRIZToolResponse:
    """Start a new TRIZ guided workflow session"""
    try:
        # Create new session
        session = ProblemSession(
            workflow_type=WorkflowType.GUIDED,
            current_stage=WorkflowStage.PROBLEM_DEFINITION
        )
        
        # Cache and save session
        _active_sessions[session.session_id] = session
        session.save_to_file(SESSIONS_DIR)
        
        # Prepare response
        response_data = {
            "session_id": session.session_id,
            "stage": session.current_stage.value,
            "next_prompt": "Please describe your technical problem or challenge. What are you trying to achieve? What are the current limitations?",
            "available_commands": ["continue", "reset", "help"],
            "workflow_type": session.workflow_type.value,
        }
        
        return TRIZToolResponse(
            success=True,
            message="TRIZ workflow session started successfully",
            data=response_data,
            session_id=session.session_id,
            stage=session.current_stage
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to start workflow: {str(e)}",
            data={}
        )


def triz_workflow_continue(session_id: str, user_input: str) -> TRIZToolResponse:
    """Continue an existing TRIZ workflow session"""
    try:
        # Load session
        session = _get_or_load_session(session_id)
        if not session:
            return TRIZToolResponse(
                success=False,
                message=f"Session not found: {session_id}",
                data={}
            )
        
        # Process input based on current stage
        session.add_user_response(session.current_stage.value, user_input)
        next_prompt = ""
        
        if session.current_stage == WorkflowStage.PROBLEM_DEFINITION:
            session.session_data.problem_statement = user_input
            next_prompt = "What is your Ideal Final Result (IFR)? Describe what the perfect solution would look like without considering current limitations."
            session.advance_stage()
            
        elif session.current_stage == WorkflowStage.CONTRADICTION_ANALYSIS:
            session.session_data.ideal_final_result = user_input
            next_prompt = "What are the main contradictions in your system? What improves when you try to solve the problem, and what gets worse?"
            session.advance_stage()
            
        elif session.current_stage == WorkflowStage.PRINCIPLE_SELECTION:
            # Parse contradictions from user input
            session.session_data.contradictions.append({"description": user_input})
            next_prompt = "Based on your contradictions, we've identified relevant TRIZ principles. Would you like to explore specific principles or generate solution concepts?"
            session.advance_stage()
            
        elif session.current_stage == WorkflowStage.SOLUTION_GENERATION:
            next_prompt = "Let's generate solution concepts using TRIZ principles. Which aspects of your problem are most critical to address?"
            session.advance_stage()
            
        elif session.current_stage == WorkflowStage.EVALUATION:
            next_prompt = "Please evaluate the proposed solutions. Which criteria are most important: feasibility, effectiveness, or innovation?"
            session.advance_stage()
            
        elif session.current_stage == WorkflowStage.COMPLETED:
            next_prompt = "Workflow completed. You can reset to start over or review your results."
        
        # Save updated session
        session.save_to_file(SESSIONS_DIR)
        
        # Prepare response
        response_data = {
            "session_id": session.session_id,
            "stage": session.current_stage.value,
            "next_prompt": next_prompt,
            "problem_statement": session.session_data.problem_statement,
            "session_data": session.session_data.__dict__,
        }
        
        if session.current_stage == WorkflowStage.COMPLETED:
            response_data["completed"] = True
        
        return TRIZToolResponse(
            success=True,
            message=f"Workflow continued to {session.current_stage.value}",
            data=response_data,
            session_id=session.session_id,
            stage=session.current_stage
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to continue workflow: {str(e)}",
            data={}
        )


def triz_workflow_reset(session_id: str) -> TRIZToolResponse:
    """Reset a TRIZ workflow session to beginning"""
    try:
        # Load session
        session = _get_or_load_session(session_id)
        if not session:
            return TRIZToolResponse(
                success=False,
                message=f"Session not found: {session_id}",
                data={}
            )
        
        # Reset session
        session.reset()
        session.save_to_file(SESSIONS_DIR)
        
        # Prepare response
        response_data = {
            "session_id": session.session_id,
            "stage": session.current_stage.value,
            "message": "Session reset to problem definition stage",
            "next_prompt": "Please describe your technical problem or challenge. What are you trying to achieve?",
        }
        
        return TRIZToolResponse(
            success=True,
            message="Workflow session reset successfully",
            data=response_data,
            session_id=session.session_id,
            stage=session.current_stage
        )
        
    except Exception as e:
        return TRIZToolResponse(
            success=False,
            message=f"Failed to reset workflow: {str(e)}",
            data={}
        )


def _get_or_load_session(session_id: str) -> Optional[ProblemSession]:
    """Get session from cache or load from file"""
    # Check cache first
    if session_id in _active_sessions:
        return _active_sessions[session_id]
    
    # Try to load from file
    session_file = SESSIONS_DIR / f"{session_id}.json"
    session = ProblemSession.load_from_file(session_file)
    
    if session:
        _active_sessions[session_id] = session
    
    return session


def triz_workflow_status(session_id: str) -> Dict[str, Any]:
    """
    Get current workflow status.
    
    Args:
        session_id: The session ID to check
        
    Returns:
        Dictionary with current workflow status
    """
    try:
        session = _get_or_load_session(session_id)
        
        if not session:
            return {
                "success": False,
                "message": "No active workflow found",
                "data": {},
                "session_id": session_id
            }
        
        return {
            "success": True,
            "message": f"Workflow is at stage: {session.current_stage.value}",
            "data": {
                "session_id": session_id,
                "current_stage": session.current_stage.value,
                "problem_statement": session.problem_statement,
                "ideal_final_result": session.ideal_final_result,
                "contradictions": [c.to_dict() for c in session.contradictions] if session.contradictions else [],
                "selected_principles": session.selected_principles,
                "solution_concepts": [s.to_dict() for s in session.solution_concepts] if session.solution_concepts else []
            },
            "session_id": session_id,
            "stage": session.current_stage.value
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get workflow status: {str(e)}",
            "data": {},
            "session_id": session_id
        }