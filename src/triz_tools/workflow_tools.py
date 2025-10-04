"""
TRIZ Workflow Tools (T037)
Implementation of guided workflow functions
NOW INTEGRATED WITH ACTUAL TRIZ ANALYSIS
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import uuid

from .models import (
    TRIZToolResponse,
    ProblemSession,
    WorkflowStage,
    WorkflowType,
)
from .services.traceability_logger import TraceabilityLogger
from .solve_tools import (
    extract_contradictions,
    generate_ideal_final_result,
    select_top_principles,
    generate_solution_concepts,
)
from .knowledge_base import load_principles_from_file


# Session storage directory
SESSIONS_DIR = Path.home() / ".triz_sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

# Active sessions cache
_active_sessions: Dict[str, ProblemSession] = {}

# Traceability loggers cache
_trackers: Dict[str, TraceabilityLogger] = {}


def triz_workflow_start() -> TRIZToolResponse:
    """Start a new TRIZ guided workflow session"""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())

        # Create new session
        session = ProblemSession(
            session_id=session_id,
            problem_statement="",  # Will be filled in first step
            workflow_type=WorkflowType.GUIDED,
            current_stage=WorkflowStage.PROBLEM_DEFINITION,
        )

        # Cache and save session
        _active_sessions[session.session_id] = session
        session.save_to_file(SESSIONS_DIR)

        # Initialize traceability logger
        tracker = TraceabilityLogger(session.session_id)
        _trackers[session.session_id] = tracker

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
            stage=session.current_stage,
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False, message=f"Failed to start workflow: {str(e)}", data={}
        )


def triz_workflow_continue(session_id: str, user_input: str) -> TRIZToolResponse:
    """Continue an existing TRIZ workflow session"""
    try:
        # Load session
        session = _get_or_load_session(session_id)
        if not session:
            return TRIZToolResponse(
                success=False, message=f"Session not found: {session_id}", data={}
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
            # ACTUAL TRIZ ANALYSIS: Extract contradictions from problem
            problem_text = session.session_data.problem_statement
            contradictions = extract_contradictions(problem_text + " " + user_input)

            # Store contradictions
            session.session_data.contradictions = contradictions[:5]  # Top 5

            # ACTUAL TRIZ ANALYSIS: Select principles based on contradictions
            principles = select_top_principles(contradictions, problem_text)
            session.session_data.selected_principles = [p["principle_id"] for p in principles]

            # Load principle details
            knowledge_base = load_principles_from_file()
            principle_details = []
            for p in principles:
                principle = knowledge_base.get_principle(p["principle_id"])
                if principle:
                    principle_details.append({
                        "id": p["principle_id"],
                        "name": principle.principle_name,
                        "description": principle.description,
                        "relevance": p["relevance_score"]
                    })

            next_prompt = f"""Based on the contradictions identified, here are the most relevant TRIZ principles:

{_format_principles(principle_details)}

Would you like to proceed with generating solution concepts based on these principles?"""
            session.advance_stage()

        elif session.current_stage == WorkflowStage.SOLUTION_GENERATION:
            # ACTUAL TRIZ ANALYSIS: Generate solutions
            problem_text = session.session_data.problem_statement
            contradictions = session.session_data.contradictions

            # Get top principles
            principles = select_top_principles(contradictions, problem_text)

            # Generate solutions
            solutions = generate_solution_concepts(problem_text, principles, contradictions)
            session.session_data.solutions = solutions

            # Format solutions for presentation
            solutions_text = _format_solutions(solutions)

            next_prompt = f"""Generated {len(solutions)} solution concepts:

{solutions_text}

Please evaluate these solutions. Which criteria are most important for your situation: feasibility, effectiveness, or innovation?"""
            session.advance_stage()

        elif session.current_stage == WorkflowStage.EVALUATION:
            # Store user evaluation criteria
            session.session_data.evaluation_criteria = user_input

            next_prompt = f"""Workflow completed!

Summary:
- Problem: {session.session_data.problem_statement[:100]}...
- IFR: {session.session_data.ideal_final_result[:100]}...
- Contradictions Found: {len(session.session_data.contradictions)}
- Principles Applied: {len(session.session_data.selected_principles)}
- Solutions Generated: {len(session.session_data.solutions)}

Your evaluation criteria: {user_input}

You can review the complete analysis in the session data."""
            session.advance_stage()

        elif session.current_stage == WorkflowStage.COMPLETED:
            next_prompt = "Workflow completed. You can reset to start over or review your results."

        # Save updated session
        session.save_to_file(SESSIONS_DIR)

        # Log to traceability system
        if session_id not in _trackers:
            _trackers[session_id] = TraceabilityLogger.load_session(session_id)

        tracker = _trackers[session_id]

        # Log the problem statement when first provided
        if (
            session.current_stage != WorkflowStage.PROBLEM_DEFINITION
            and session.session_data.problem_statement
        ):
            if not tracker.manifest.get("problem_statement"):
                tracker.log_problem(session.session_data.problem_statement)

        # Log step
        stage_number = list(WorkflowStage).index(session.current_stage)
        tracker.log_step(
            step_number=stage_number,
            step_name=session.current_stage.value,
            user_input=user_input,
            system_response=next_prompt,
            findings_generated=[],
            sources_used=[],
        )

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
            stage=session.current_stage,
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False, message=f"Failed to continue workflow: {str(e)}", data={}
        )


def triz_workflow_reset(session_id: str) -> TRIZToolResponse:
    """Reset a TRIZ workflow session to beginning"""
    try:
        # Load session
        session = _get_or_load_session(session_id)
        if not session:
            return TRIZToolResponse(
                success=False, message=f"Session not found: {session_id}", data={}
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
            stage=session.current_stage,
        )

    except Exception as e:
        return TRIZToolResponse(
            success=False, message=f"Failed to reset workflow: {str(e)}", data={}
        )


def _get_or_load_session(session_id: str) -> Optional[ProblemSession]:
    """Get session from cache or load from file"""
    # Check cache first
    if session_id in _active_sessions:
        return _active_sessions[session_id]

    # Try to load from file
    session_file = SESSIONS_DIR / f"{session_id}.json"

    if not session_file.exists():
        return None

    try:
        session = ProblemSession.load_from_file(session_file)
        if session:
            _active_sessions[session_id] = session
        return session
    except Exception:
        return None


def _format_principles(principles: List[Dict[str, Any]]) -> str:
    """Format principles for display"""
    if not principles:
        return "No principles identified."

    formatted = []
    for i, p in enumerate(principles[:5], 1):  # Top 5
        formatted.append(
            f"{i}. **Principle {p['id']}: {p['name']}** (Relevance: {p['relevance']:.2f})\n"
            f"   {p['description'][:200]}..."
        )

    return "\n\n".join(formatted)


def _format_solutions(solutions: List[Dict[str, Any]]) -> str:
    """Format solutions for display"""
    if not solutions:
        return "No solutions generated."

    formatted = []
    for i, sol in enumerate(solutions[:5], 1):  # Top 5
        title = sol.get("title", f"Solution {i}")
        desc = sol.get("description", "No description")
        principle = sol.get("principle_name", "Unknown principle")
        feasibility = sol.get("feasibility_score", 0.0)

        formatted.append(
            f"{i}. **{title}** (Feasibility: {feasibility:.2f})\n"
            f"   Based on: {principle}\n"
            f"   {desc[:300]}..."
        )

    return "\n\n".join(formatted)


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
                "session_id": session_id,
            }

        return {
            "success": True,
            "message": f"Workflow is at stage: {session.current_stage.value}",
            "data": {
                "session_id": session_id,
                "current_stage": session.current_stage.value,
                "problem_statement": session.problem_statement,
                "ideal_final_result": session.ideal_final_result,
                "contradictions": [c.to_dict() for c in session.contradictions]
                if session.contradictions
                else [],
                "selected_principles": session.selected_principles,
                "solution_concepts": [s.to_dict() for s in session.solution_concepts]
                if session.solution_concepts
                else [],
            },
            "session_id": session_id,
            "stage": session.current_stage.value,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get workflow status: {str(e)}",
            "data": {},
            "session_id": session_id,
        }
