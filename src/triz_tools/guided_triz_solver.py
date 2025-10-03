"""
Guided TRIZ Solver - Academic Methodology Implementation
Based on: "TRIZ: An Alternate Way to Solve Problem for Student" (Tee et al., 2017)

This implements the 5-phase TRIZ academic process as 33 guided research steps:
    PHASE 1: Problem Analysis (Steps 1-8)
    PHASE 2: Parameterization (Steps 9-14)
    PHASE 3: Contradiction Matrix (Steps 15-18)
    PHASE 4: Principle Deep Research (Steps 19-28)
    PHASE 5: Solution Synthesis (Steps 29-33)

Each step returns research instructions for the AI, not solutions.
The AI must perform 33 iterations of research and validation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from pathlib import Path


class TRIZPhase(Enum):
    """5 phases of academic TRIZ methodology"""

    PROBLEM_ANALYSIS = "problem_analysis"
    PARAMETERIZATION = "parameterization"
    CONTRADICTION_MATRIX = "contradiction_matrix"
    PRINCIPLE_RESEARCH = "principle_research"
    SOLUTION_SYNTHESIS = "solution_synthesis"


class StepStatus(Enum):
    """Status of each step"""

    PENDING = "pending"
    AWAITING_RESEARCH = "awaiting_research"
    RESEARCH_SUBMITTED = "research_submitted"
    VALIDATED = "validated"
    SKIPPED = "skipped"


@dataclass
class StepInstruction:
    """Instructions for AI to perform research"""

    task: str
    search_queries: List[str]
    extract_requirements: List[str]
    validation_criteria: str
    expected_output_format: str
    why_this_matters: str


@dataclass
class TRIZStep:
    """A single step in the 33-step guided TRIZ process"""

    step_number: int
    phase: TRIZPhase
    title: str
    status: StepStatus
    instruction: Optional[StepInstruction] = None
    findings: Dict[str, Any] = field(default_factory=dict)
    validation_result: Optional[str] = None


@dataclass
class TRIZGuidedSession:
    """Complete guided TRIZ research session"""

    session_id: str
    problem: str
    current_step: int
    steps: List[TRIZStep]
    accumulated_knowledge: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class GuidedTRIZSolver:
    """
    Guided TRIZ Solver - implements academic 33-step methodology

    This class generates research instructions step-by-step,
    validates findings, and guides the AI through complete TRIZ analysis.
    """

    def __init__(self):
        self.sessions_dir = Path(__file__).parent.parent / "data" / "guided_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def start_guided_session(self, problem: str) -> Dict[str, Any]:
        """
        Start a new guided TRIZ research session.
        Returns instructions for Step 1.

        Args:
            problem: Problem description

        Returns:
            Dict with session_id and first step instructions
        """
        import uuid
        from datetime import datetime

        session_id = str(uuid.uuid4())[:8]

        # Initialize all 33 steps
        steps = self._initialize_33_steps()

        session = TRIZGuidedSession(
            session_id=session_id,
            problem=problem,
            current_step=1,
            steps=steps,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        # Save session
        self._save_session(session)

        # Generate Step 1 instructions
        step_1_instruction = self._generate_step_instruction(1, problem, {})
        session.steps[0].instruction = step_1_instruction
        session.steps[0].status = StepStatus.AWAITING_RESEARCH
        self._save_session(session)

        return {
            "session_id": session_id,
            "total_steps": 33,
            "current_step": 1,
            "phase": "PROBLEM_ANALYSIS",
            "instruction": self._format_instruction(step_1_instruction),
            "context": {"problem": problem, "progress": "1/33 steps (3%)"},
        }

    def submit_research(
        self, session_id: str, findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit research findings for current step and get next step instructions.

        Args:
            session_id: Session ID from start_guided_session
            findings: Research findings from AI (must match extract_requirements)

        Returns:
            Dict with validation result and next step instructions (or final solution)
        """
        session = self._load_session(session_id)

        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        current_step_num = session.current_step
        current_step = session.steps[current_step_num - 1]

        # Validate findings
        validation = self._validate_findings(current_step, findings)

        if not validation["valid"]:
            return {
                "success": False,
                "validation_failed": True,
                "current_step": current_step_num,
                "error": validation["error"],
                "instruction": self._format_instruction(current_step.instruction),
                "hint": validation.get("hint", ""),
                "progress": f"{current_step_num}/33 steps ({int(current_step_num / 33 * 100)}%)",
            }

        # Store findings
        current_step.findings = findings
        current_step.status = StepStatus.VALIDATED
        current_step.validation_result = validation["message"]

        # Update accumulated knowledge
        self._update_accumulated_knowledge(session, current_step_num, findings)

        # Check if final step
        if current_step_num >= 33:
            # Generate final solution
            final_solution = self._generate_final_solution(session)
            session.steps[current_step_num - 1].status = StepStatus.VALIDATED
            self._save_session(session)

            return {
                "success": True,
                "completed": True,
                "total_steps": 33,
                "final_solution": final_solution,
                "session_summary": self._generate_session_summary(session),
            }

        # Move to next step
        next_step_num = current_step_num + 1
        session.current_step = next_step_num

        # Generate next step instruction
        next_step = session.steps[next_step_num - 1]
        next_instruction = self._generate_step_instruction(
            next_step_num, session.problem, session.accumulated_knowledge
        )
        next_step.instruction = next_instruction
        next_step.status = StepStatus.AWAITING_RESEARCH

        from datetime import datetime

        session.updated_at = datetime.now().isoformat()
        self._save_session(session)

        return {
            "success": True,
            "validation": validation["message"],
            "step_completed": current_step_num,
            "current_step": next_step_num,
            "total_steps": 33,
            "phase": next_step.phase.value,
            "instruction": self._format_instruction(next_instruction),
            "context": session.accumulated_knowledge,
            "progress": f"{next_step_num}/33 steps ({int(next_step_num / 33 * 100)}%)",
        }

    def _initialize_33_steps(self) -> List[TRIZStep]:
        """Initialize all 33 steps with metadata"""
        steps = []

        # PHASE 1: Problem Analysis (Steps 1-8)
        phase1_titles = [
            "Identify main function of system",
            "Extract auxiliary functions",
            "Identify harmful functions",
            "Identify insufficient functions",
            "List available substance resources",
            "List field resources (energy/forces)",
            "Formulate Ideal Final Result (IFR)",
            "Validate problem understanding",
        ]

        for i, title in enumerate(phase1_titles, 1):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.PROBLEM_ANALYSIS,
                    title=title,
                    status=StepStatus.PENDING,
                )
            )

        # PHASE 2: Parameterization (Steps 9-14)
        phase2_titles = [
            "Identify what is improving",
            "Extract specific improvement metrics",
            "Identify what is worsening",
            "Extract specific worsening metrics",
            "Map improving to TRIZ 39 Parameters",
            "Map worsening to TRIZ 39 Parameters",
        ]

        for i, title in enumerate(phase2_titles, 9):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.PARAMETERIZATION,
                    title=title,
                    status=StepStatus.PENDING,
                )
            )

        # PHASE 3: Contradiction Matrix (Steps 15-18)
        phase3_titles = [
            "Lookup contradiction matrix intersection",
            "Extract recommended principle numbers",
            "Research why these principles recommended",
            "Rank principles by applicability",
        ]

        for i, title in enumerate(phase3_titles, 15):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.CONTRADICTION_MATRIX,
                    title=title,
                    status=StepStatus.PENDING,
                )
            )

        # PHASE 4: Principle Deep Research (Steps 19-28) - THE CORE!
        phase4_titles = [
            "Read Principle #1 full description",
            "Find examples of Principle #1",
            "Extract sub-principles of Principle #1",
            "Read Principle #2 full description",
            "Find examples of Principle #2",
            "Extract sub-principles of Principle #2",
            "Deep materials research (if applicable)",
            "Extract material properties from books",
            "Create material comparison tables",
            "Find cross-domain analogies",
        ]

        for i, title in enumerate(phase4_titles, 19):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.PRINCIPLE_RESEARCH,
                    title=title,
                    status=StepStatus.PENDING,
                )
            )

        # PHASE 5: Solution Synthesis (Steps 29-33)
        phase5_titles = [
            "Convert general solutions to specific solutions",
            "Combine multiple principles synergistically",
            "Validate solutions against IFR",
            "Assess implementation feasibility",
            "Generate final recommendation with evidence",
        ]

        for i, title in enumerate(phase5_titles, 29):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.SOLUTION_SYNTHESIS,
                    title=title,
                    status=StepStatus.PENDING,
                )
            )

        return steps

    def _generate_step_instruction(
        self, step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
    ) -> StepInstruction:
        """Generate specific instruction for each step"""

        # Import step generators
        from triz_tools.guided_steps import (
            phase1_instructions,
            phase2_instructions,
            phase3_instructions,
            phase4_instructions,
            phase5_instructions,
        )

        if 1 <= step_num <= 8:
            return phase1_instructions.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 9 <= step_num <= 14:
            return phase2_instructions.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 15 <= step_num <= 18:
            return phase3_instructions.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 19 <= step_num <= 28:
            return phase4_instructions.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 29 <= step_num <= 33:
            return phase5_instructions.generate(
                step_num, problem, accumulated_knowledge
            )
        else:
            raise ValueError(f"Invalid step number: {step_num}")

    def _validate_findings(
        self, step: TRIZStep, findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate if AI's findings meet requirements"""

        if not step.instruction:
            return {"valid": False, "error": "No instruction found for step"}

        extract_reqs = step.instruction.extract_requirements

        # Check if all required fields present
        missing_fields = []
        for req in extract_reqs:
            # Convert requirement to likely field name
            field_key = req.lower().replace("?", "").replace(" ", "_")[:30]
            if field_key not in findings and req not in findings:
                missing_fields.append(req)

        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required findings: {missing_fields}",
                "hint": f"Your findings must include: {extract_reqs}",
            }

        # Basic content validation
        for key, value in findings.items():
            if isinstance(value, str) and len(value.strip()) < 10:
                return {
                    "valid": False,
                    "error": f"Finding '{key}' is too short. Provide detailed research.",
                    "hint": "Search the knowledge base thoroughly and extract specific information.",
                }

        return {
            "valid": True,
            "message": f"✅ Step {step.step_number} validated: {step.title}",
        }

    def _update_accumulated_knowledge(
        self, session: TRIZGuidedSession, step_num: int, findings: Dict[str, Any]
    ):
        """Update session's accumulated knowledge from step findings"""
        step_key = f"step_{step_num}"
        session.accumulated_knowledge[step_key] = findings

        # Also store by semantic keys for easy access
        if step_num == 1:
            session.accumulated_knowledge["main_function"] = findings.get(
                "main_function"
            )
        elif step_num == 9:
            session.accumulated_knowledge["improving_parameter"] = findings.get(
                "improving"
            )
        elif step_num == 11:
            session.accumulated_knowledge["worsening_parameter"] = findings.get(
                "worsening"
            )
        elif step_num == 15:
            session.accumulated_knowledge["contradiction_matrix_result"] = findings
        # ... continue for key steps

    def _generate_final_solution(self, session: TRIZGuidedSession) -> Dict[str, Any]:
        """Generate final solution from all 33 steps of research"""

        return {
            "problem": session.problem,
            "triz_analysis_complete": True,
            "total_research_steps": 33,
            "phases_completed": 5,
            "solution": {
                "recommended_approach": session.accumulated_knowledge.get(
                    "step_29", {}
                ),
                "principles_applied": session.accumulated_knowledge.get("step_15", {}),
                "materials_recommendation": session.accumulated_knowledge.get(
                    "step_25", {}
                ),
                "implementation_plan": session.accumulated_knowledge.get("step_32", {}),
                "final_synthesis": session.accumulated_knowledge.get("step_33", {}),
            },
            "evidence_base": {
                "function_analysis": session.accumulated_knowledge.get("step_1", {}),
                "contradiction_identified": {
                    "improving": session.accumulated_knowledge.get("step_9", {}),
                    "worsening": session.accumulated_knowledge.get("step_11", {}),
                },
                "principles_researched": [
                    session.accumulated_knowledge.get("step_19", {}),
                    session.accumulated_knowledge.get("step_22", {}),
                ],
                "materials_research": session.accumulated_knowledge.get("step_25", {}),
            },
        }

    def _generate_session_summary(self, session: TRIZGuidedSession) -> Dict[str, Any]:
        """Generate summary of entire research session"""

        validated_steps = sum(
            1 for s in session.steps if s.status == StepStatus.VALIDATED
        )

        return {
            "session_id": session.session_id,
            "problem": session.problem,
            "total_steps": len(session.steps),
            "completed_steps": validated_steps,
            "phases": {
                "problem_analysis": [
                    s.title
                    for s in session.steps[0:8]
                    if s.status == StepStatus.VALIDATED
                ],
                "parameterization": [
                    s.title
                    for s in session.steps[8:14]
                    if s.status == StepStatus.VALIDATED
                ],
                "contradiction_matrix": [
                    s.title
                    for s in session.steps[14:18]
                    if s.status == StepStatus.VALIDATED
                ],
                "principle_research": [
                    s.title
                    for s in session.steps[18:28]
                    if s.status == StepStatus.VALIDATED
                ],
                "solution_synthesis": [
                    s.title
                    for s in session.steps[28:33]
                    if s.status == StepStatus.VALIDATED
                ],
            },
            "created_at": session.created_at,
            "completed_at": session.updated_at,
        }

    def _format_instruction(self, instruction: StepInstruction) -> Dict[str, Any]:
        """Format instruction for display"""
        return {
            "task": instruction.task,
            "search_queries": instruction.search_queries,
            "extract": instruction.extract_requirements,
            "validation": instruction.validation_criteria,
            "format": instruction.expected_output_format,
            "why": instruction.why_this_matters,
        }

    def _save_session(self, session: TRIZGuidedSession):
        """Save session to JSON file"""
        filepath = self.sessions_dir / f"{session.session_id}.json"

        # Convert to dict
        session_dict = {
            "session_id": session.session_id,
            "problem": session.problem,
            "current_step": session.current_step,
            "accumulated_knowledge": session.accumulated_knowledge,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "steps": [
                {
                    "step_number": s.step_number,
                    "phase": s.phase.value,
                    "title": s.title,
                    "status": s.status.value,
                    "findings": s.findings,
                    "validation_result": s.validation_result,
                }
                for s in session.steps
            ],
        }

        with open(filepath, "w") as f:
            json.dump(session_dict, f, indent=2)

    def _load_session(self, session_id: str) -> Optional[TRIZGuidedSession]:
        """Load session from JSON file"""
        filepath = self.sessions_dir / f"{session_id}.json"

        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            data = json.load(f)

        # Reconstruct steps
        steps = []
        for s in data["steps"]:
            step = TRIZStep(
                step_number=s["step_number"],
                phase=TRIZPhase(s["phase"]),
                title=s["title"],
                status=StepStatus(s["status"]),
                findings=s["findings"],
                validation_result=s.get("validation_result"),
            )
            steps.append(step)

        return TRIZGuidedSession(
            session_id=data["session_id"],
            problem=data["problem"],
            current_step=data["current_step"],
            steps=steps,
            accumulated_knowledge=data["accumulated_knowledge"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


# Public API functions for MCP integration
def start_guided_triz_research(problem: str) -> Dict[str, Any]:
    """
    Start a guided TRIZ research session.

    Args:
        problem: Problem description

    Returns:
        Session ID and first step instructions
    """
    solver = GuidedTRIZSolver()
    return solver.start_guided_session(problem)


def submit_research_findings(
    session_id: str, findings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Submit research findings and get next step.

    Args:
        session_id: Session ID from start_guided_triz_research
        findings: Research findings dictionary

    Returns:
        Validation result and next step instructions (or final solution)
    """
    solver = GuidedTRIZSolver()
    return solver.submit_research(session_id, findings)
