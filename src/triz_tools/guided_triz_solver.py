"""
Complete TRIZ Guided Solver - 60 Steps
Official TRIZ Methodology Implementation

This implements the complete 6-phase TRIZ process as 60 guided research steps.
Each step returns research instructions for the AI, NOT solutions.
The AI must perform 60 iterations of research and validation.

PHASES:
    PHASE 1: Understand & Scope (Steps 1-10) - 9 Boxes + Ideality Audit
    PHASE 2: Define Ideal (Steps 11-16) - Ideal Outcome + Resources
    PHASE 3: Function Analysis (Steps 17-26) - Subject-Action-Object + Contradictions
    PHASE 4: Select Tools (Steps 27-32) - Tool Selection Logic
    PHASE 5: Generate Solutions (Steps 33-50) - 40 Principles + Standard Solutions + Effects + Materials
    PHASE 6: Rank & Implement (Steps 51-60) - Ideality Plot + Implementation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import uuid
from datetime import datetime

from .triz_models import (
    TRIZGuidedSession,
    TRIZStep,
    TRIZPhase,
    StepStatus,
    StepInstruction,
    NineBoxes,
    Ideality,
    IdealOutcome,
    FunctionMap,
    TechnicalContradiction,
    PhysicalContradiction,
    SolutionConcept,
    Resource,
)
from .services.traceability_logger import TraceabilityLogger


class GuidedTRIZSolver:
    """
    Complete TRIZ Guided Solver - 60 steps

    This class does NOT solve problems directly.
    It GUIDES the AI through 60 research steps to discover solutions.
    """

    def __init__(self):
        self.sessions_dir = Path(__file__).parent.parent / "data" / "guided_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.trackers: Dict[str, TraceabilityLogger] = {}  # Track loggers per session

    def start_guided_session(self, problem: str) -> Dict[str, Any]:
        """
        Start new guided TRIZ research session.

        Returns:
            Dict with session_id and Step 1 instructions
        """
        session_id = str(uuid.uuid4())[:8]

        # Initialize all 60 steps
        steps = self._initialize_60_steps()

        session = TRIZGuidedSession(
            session_id=session_id,
            problem=problem,
            current_step=1,
            steps=steps,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        # Generate Step 1 instruction
        from .guided_steps import phase1_understand_scope

        step_1_instruction = phase1_understand_scope.generate(1, problem, {})

        session.steps[0].instruction = step_1_instruction
        session.steps[0].status = StepStatus.AWAITING_RESEARCH

        self._save_session(session)

        # Initialize traceability logger
        tracker = TraceabilityLogger(session_id)
        tracker.log_problem(problem)
        self.trackers[session_id] = tracker

        return {
            "session_id": session_id,
            "total_steps": 60,
            "current_step": 1,
            "phase": "UNDERSTAND_SCOPE",
            "phase_description": "Create 9 Boxes context map and calculate current Ideality",
            "instruction": self._format_instruction(step_1_instruction),
            "context": {
                "problem": problem,
                "progress": "1/60 steps (2%)",
                "phase_progress": "Step 1 of 10 in Phase 1",
            },
        }

    def submit_research(
        self, session_id: str, findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit research findings for current step.

        Args:
            session_id: Session ID
            findings: Research findings (must match extract_requirements)

        Returns:
            Validation result and next step instructions (or final solution if step 60)
        """
        session = self._load_session(session_id)

        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        # Get or create traceability logger
        if session_id not in self.trackers:
            self.trackers[session_id] = TraceabilityLogger.load_session(session_id)

        current_step_num = session.current_step
        current_step = session.steps[current_step_num - 1]

        # Ensure instruction is loaded (might be None if session was loaded from disk)
        if not current_step.instruction:
            current_step.instruction = self._generate_step_instruction(
                current_step_num, session.problem, session.accumulated_knowledge
            )

        # Validate findings
        validation = self._validate_findings(current_step, findings)

        if not validation["valid"]:
            return {
                "success": False,
                "validation_failed": True,
                "current_step": current_step_num,
                "error": validation["error"],
                "hint": validation.get("hint", ""),
                "instruction": self._format_instruction(current_step.instruction),
                "progress": f"{current_step_num}/60 steps ({int(current_step_num / 60 * 100)}%)",
            }

        # Store validated findings
        current_step.findings = findings
        current_step.status = StepStatus.VALIDATED
        current_step.validation_result = validation["message"]

        # Update accumulated knowledge
        self._update_accumulated_knowledge(session, current_step_num, findings)

        # Update TRIZ artifacts
        self._update_triz_artifacts(session, current_step_num, findings)

        # Log to traceability system
        tracker = self.trackers[session_id]
        source_ids = self._log_sources(tracker, findings)
        finding_ids = self._log_findings(
            tracker, current_step_num, findings, source_ids
        )
        tracker.log_step(
            step_number=current_step_num,
            step_name=current_step.instruction.step_name
            if current_step.instruction
            else f"Step {current_step_num}",
            user_input=json.dumps(findings, indent=2),
            system_response=validation["message"],
            findings_generated=finding_ids,
            sources_used=source_ids,
        )

        # Check if final step
        if current_step_num >= 60:
            final_solution = self._generate_final_solution(session)
            self._save_session(session)

            # Generate final traceability report
            tracker = self.trackers[session_id]
            solution_file = tracker.generate_final_solution(final_solution)
            session_summary = tracker.get_session_summary()

            return {
                "success": True,
                "completed": True,
                "total_steps": 60,
                "final_solution": final_solution,
                "session_summary": session_summary,
                "traceability_files": session_summary["files"],
                "triz_artifacts": {
                    "nine_boxes": session.nine_boxes,
                    "current_ideality": session.current_ideality,
                    "ideal_outcome": session.ideal_outcome,
                    "function_map": session.function_map,
                    "contradictions": {
                        "technical": session.technical_contradictions,
                        "physical": session.physical_contradictions,
                    },
                    "solutions": session.solution_concepts,
                },
            }

        # Move to next step
        next_step_num = current_step_num + 1
        session.current_step = next_step_num

        # Generate next step instruction
        next_instruction = self._generate_step_instruction(
            next_step_num, session.problem, session.accumulated_knowledge
        )

        next_step = session.steps[next_step_num - 1]
        next_step.instruction = next_instruction
        next_step.status = StepStatus.AWAITING_RESEARCH

        session.updated_at = datetime.now().isoformat()
        self._save_session(session)

        return {
            "success": True,
            "validation": validation["message"],
            "step_completed": current_step_num,
            "current_step": next_step_num,
            "total_steps": 60,
            "phase": session.current_phase.value,
            "phase_description": self._get_phase_description(session.current_phase),
            "instruction": self._format_instruction(next_instruction),
            "context": session.accumulated_knowledge,
            "progress": f"{next_step_num}/60 steps ({int(next_step_num / 60 * 100)}%)",
            "phase_progress": self._get_phase_progress(next_step_num),
        }

    def _initialize_60_steps(self) -> List[TRIZStep]:
        """Initialize all 60 steps with metadata"""
        steps = []

        # PHASE 1: Understand & Scope (Steps 1-10)
        phase1_titles = [
            "Create 9 Boxes context map",
            "Research Sub-System components",
            "Research Super-System environment",
            "Analyze Past evolution",
            "Analyze Future trends",
            "Identify all current Benefits",
            "Identify all current Costs",
            "Identify all current Harms",
            "Calculate current Ideality score",
            "Identify root causes from 9 Boxes",
        ]
        for i, title in enumerate(phase1_titles, 1):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.UNDERSTAND_SCOPE,
                    title=title,
                    status=StepStatus.PENDING,
                    triz_tool="9 Boxes + Ideality Audit",
                )
            )

        # PHASE 2: Define Ideal (Steps 11-16)
        phase2_titles = [
            "Create Ideal Outcome wish list",
            "Research ideal systems in other domains",
            "Identify Resources (Substance, Field, Space, Time, Information)",
            "Research resource utilization examples",
            "Define Ideal System in 9 Boxes",
            "Calculate Ideal Ideality target",
        ]
        for i, title in enumerate(phase2_titles, 11):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.DEFINE_IDEAL,
                    title=title,
                    status=StepStatus.PENDING,
                    triz_tool="Ideal Outcome + Resources",
                )
            )

        # PHASE 3: Function Analysis (Steps 17-26)
        phase3_titles = [
            "Map all Subject-Action-Object relationships",
            "Categorize: Useful functions",
            "Categorize: Insufficient functions",
            "Categorize: Excessive functions",
            "Categorize: Harmful functions",
            "Research harm elimination examples",
            "Identify Technical Contradictions",
            "Identify Physical Contradictions",
            "Research contradiction resolution examples",
            "Prioritize problems to solve",
        ]
        for i, title in enumerate(phase3_titles, 17):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.FUNCTION_ANALYSIS,
                    title=title,
                    status=StepStatus.PENDING,
                    triz_tool="Function Analysis + Contradictions",
                )
            )

        # PHASE 4: Select Tools (Steps 27-32)
        phase4_titles = [
            "Match problems to TRIZ tool categories",
            "Map contradictions to 39 Parameters",
            "Lookup Contradiction Matrix",
            "Identify Standard Solutions for harms",
            "Search Effects Database for functions",
            "Research Evolution Trends",
        ]
        for i, title in enumerate(phase4_titles, 27):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.SELECT_TOOLS,
                    title=title,
                    status=StepStatus.PENDING,
                    triz_tool="Tool Selection Logic",
                )
            )

        # PHASE 5: Generate Solutions (Steps 33-50) - 18 STEPS
        phase5_titles = [
            "Deep research Principle #1",
            "Find examples of Principle #1",
            "Extract sub-principles of Principle #1",
            "Apply Principle #1 to problem",
            "Deep research Principle #2",
            "Find examples of Principle #2",
            "Extract sub-principles of Principle #2",
            "Apply Principle #2 to problem",
            "Research Principle #3 if applicable",
            "Apply Standard Solution: Eliminate harm",
            "Apply Standard Solution: Block harm",
            "Apply Standard Solution: Convert harm to benefit",
            "Apply Standard Solution: Enhance insufficient functions",
            "Research Effects Database for new functions",
            "DEEP materials research",
            "Extract material properties (density, strength, formability)",
            "Create material comparison tables",
            "Synthesize complete solution concepts",
        ]
        for i, title in enumerate(phase5_titles, 33):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.GENERATE_SOLUTIONS,
                    title=title,
                    status=StepStatus.PENDING,
                    triz_tool="40 Principles + Standard Solutions + Effects",
                )
            )

        # PHASE 6: Rank & Implement (Steps 51-60) - 10 STEPS
        phase6_titles = [
            "Calculate Ideality for each solution",
            "Calculate expected benefits per solution",
            "Calculate expected costs per solution",
            "Calculate expected harms per solution",
            "Create Ideality Plot",
            "Categorize solutions (Implement/Improve/Research/Park)",
            "Select top 3 solutions",
            "Research implementation requirements",
            "Create implementation timeline",
            "Generate final synthesis with evidence",
        ]
        for i, title in enumerate(phase6_titles, 51):
            steps.append(
                TRIZStep(
                    step_number=i,
                    phase=TRIZPhase.RANK_IMPLEMENT,
                    title=title,
                    status=StepStatus.PENDING,
                    triz_tool="Ideality Plot + Implementation",
                )
            )

        return steps

    def _generate_step_instruction(
        self, step_num: int, problem: str, accumulated_knowledge: Dict[str, Any]
    ) -> StepInstruction:
        """Generate instruction for specific step"""
        from .guided_steps import (
            phase1_understand_scope,
            phase2_define_ideal,
            phase3_function_analysis,
            phase4_select_tools,
            phase5_generate_solutions,
            phase6_rank_implement,
        )

        if 1 <= step_num <= 10:
            return phase1_understand_scope.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 11 <= step_num <= 16:
            return phase2_define_ideal.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 17 <= step_num <= 26:
            return phase3_function_analysis.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 27 <= step_num <= 32:
            return phase4_select_tools.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 33 <= step_num <= 50:
            return phase5_generate_solutions.generate(
                step_num, problem, accumulated_knowledge
            )
        elif 51 <= step_num <= 60:
            return phase6_rank_implement.generate(
                step_num, problem, accumulated_knowledge
            )
        else:
            raise ValueError(f"Invalid step number: {step_num}")

    def _validate_findings(
        self, step: TRIZStep, findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate if findings meet requirements"""

        if not step.instruction:
            return {"valid": False, "error": "No instruction found for step"}

        extract_reqs = step.instruction.extract_requirements

        # Check if all required fields present
        missing_fields = []
        for req in extract_reqs:
            if req not in findings:
                # Try variations
                req_lower = req.lower().replace(" ", "_")
                if req_lower not in findings:
                    missing_fields.append(req)

        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required findings: {', '.join(missing_fields)}",
                "hint": f"Your findings must include all of: {', '.join(extract_reqs)}",
            }

        # Basic content validation
        for key, value in findings.items():
            if isinstance(value, str) and len(value.strip()) < 10:
                return {
                    "valid": False,
                    "error": f"Finding '{key}' is too short ({len(value)} chars). Provide detailed research with at least 50 characters.",
                    "hint": "Search the knowledge base thoroughly and extract specific, detailed information.",
                }

        return {
            "valid": True,
            "message": f"✅ Step {step.step_number} validated successfully: {step.title}",
        }

    def _update_accumulated_knowledge(
        self, session: TRIZGuidedSession, step_num: int, findings: Dict[str, Any]
    ):
        """Update session's accumulated knowledge from step findings"""
        step_key = f"step_{step_num}"
        session.accumulated_knowledge[step_key] = findings

    def _update_triz_artifacts(
        self, session: TRIZGuidedSession, step_num: int, findings: Dict[str, Any]
    ):
        """Update TRIZ artifacts (9 Boxes, Ideality, Function Map, etc.) from findings"""

        # Update 9 Boxes from steps 1-5
        if 1 <= step_num <= 5:
            if not session.nine_boxes:
                session.nine_boxes = {}

        # Update current Ideality from step 9
        if step_num == 9:
            ideality_data = findings.get("calculation", {})
            if ideality_data:
                session.current_ideality = ideality_data

        # Update Ideal Outcome from step 11
        if step_num == 11:
            ideal_data = findings.get("ideal_outcome", {})
            if ideal_data:
                session.ideal_outcome = ideal_data

        # Update Function Map from steps 17-21
        if 17 <= step_num <= 21:
            if not session.function_map:
                session.function_map = {}

        # Update Contradictions from steps 23-24
        if step_num == 23:
            tech_contradictions = findings.get("technical_contradictions", [])
            session.technical_contradictions = tech_contradictions

        if step_num == 24:
            phys_contradictions = findings.get("physical_contradictions", [])
            session.physical_contradictions = phys_contradictions

        # Update Solution Concepts from step 50
        if step_num == 50:
            solutions = findings.get("complete_solutions", [])
            session.solution_concepts = solutions

    def _generate_final_solution(self, session: TRIZGuidedSession) -> Dict[str, Any]:
        """Generate final solution from all 60 steps of research"""

        # Get final synthesis from step 60
        final_synthesis = session.accumulated_knowledge.get("step_60", {})

        return {
            "problem": session.problem,
            "methodology": "Complete TRIZ 60-Step Guided Research",
            "total_steps_completed": 60,
            "phases_completed": 6,
            "executive_summary": final_synthesis.get("executive_summary", {}),
            "triz_journey": final_synthesis.get("triz_methodology_applied", {}),
            "recommended_solution": final_synthesis.get(
                "recommended_solution_details", {}
            ),
            "supporting_evidence": final_synthesis.get("supporting_evidence", {}),
            "implementation_roadmap": final_synthesis.get("implementation_roadmap", {}),
            "future_iterations": final_synthesis.get("future_triz_iterations", {}),
            "conclusion": final_synthesis.get("conclusion", {}),
        }

    def _generate_session_summary(self, session: TRIZGuidedSession) -> Dict[str, Any]:
        """Generate summary of entire research session"""

        validated_steps = sum(
            1 for s in session.steps if s.status == StepStatus.VALIDATED
        )

        return {
            "session_id": session.session_id,
            "problem": session.problem,
            "total_steps": 60,
            "completed_steps": validated_steps,
            "completion_rate": f"{int(validated_steps / 60 * 100)}%",
            "phases_summary": {
                "phase_1_understand_scope": {
                    "steps": "1-10",
                    "completed": sum(
                        1
                        for s in session.steps[0:10]
                        if s.status == StepStatus.VALIDATED
                    ),
                    "tools_used": "9 Boxes, Ideality Audit",
                },
                "phase_2_define_ideal": {
                    "steps": "11-16",
                    "completed": sum(
                        1
                        for s in session.steps[10:16]
                        if s.status == StepStatus.VALIDATED
                    ),
                    "tools_used": "Ideal Outcome, Resources",
                },
                "phase_3_function_analysis": {
                    "steps": "17-26",
                    "completed": sum(
                        1
                        for s in session.steps[16:26]
                        if s.status == StepStatus.VALIDATED
                    ),
                    "tools_used": "Function Map, Contradictions",
                },
                "phase_4_select_tools": {
                    "steps": "27-32",
                    "completed": sum(
                        1
                        for s in session.steps[26:32]
                        if s.status == StepStatus.VALIDATED
                    ),
                    "tools_used": "Contradiction Matrix, Tool Selection",
                },
                "phase_5_generate_solutions": {
                    "steps": "33-50",
                    "completed": sum(
                        1
                        for s in session.steps[32:50]
                        if s.status == StepStatus.VALIDATED
                    ),
                    "tools_used": "40 Principles, Standard Solutions, Effects, Materials",
                },
                "phase_6_rank_implement": {
                    "steps": "51-60",
                    "completed": sum(
                        1
                        for s in session.steps[50:60]
                        if s.status == StepStatus.VALIDATED
                    ),
                    "tools_used": "Ideality Plot, Implementation Planning",
                },
            },
            "created_at": session.created_at,
            "completed_at": session.updated_at,
            "duration": "Calculated from timestamps",
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
            "related_triz_tool": getattr(instruction, "related_triz_tool", "N/A"),
        }

    def _get_phase_description(self, phase: TRIZPhase) -> str:
        """Get human-readable phase description"""
        descriptions = {
            TRIZPhase.UNDERSTAND_SCOPE: "Understand & Scope with 9 Boxes + Ideality Audit",
            TRIZPhase.DEFINE_IDEAL: "Define Ideal Outcome + Identify Resources",
            TRIZPhase.FUNCTION_ANALYSIS: "Function Analysis (Subject-Action-Object) + Contradictions",
            TRIZPhase.SELECT_TOOLS: "Select appropriate TRIZ solution tools",
            TRIZPhase.GENERATE_SOLUTIONS: "Generate Solutions using 40 Principles + Standard Solutions + Effects + Materials",
            TRIZPhase.RANK_IMPLEMENT: "Rank by Ideality Plot + Create Implementation Plan",
        }
        return descriptions.get(phase, "Unknown phase")

    def _get_phase_progress(self, step_num: int) -> str:
        """Get phase progress string"""
        if 1 <= step_num <= 10:
            return f"Step {step_num} of 10 in Phase 1 (Understand & Scope)"
        elif 11 <= step_num <= 16:
            return f"Step {step_num - 10} of 6 in Phase 2 (Define Ideal)"
        elif 17 <= step_num <= 26:
            return f"Step {step_num - 16} of 10 in Phase 3 (Function Analysis)"
        elif 27 <= step_num <= 32:
            return f"Step {step_num - 26} of 6 in Phase 4 (Select Tools)"
        elif 33 <= step_num <= 50:
            return f"Step {step_num - 32} of 18 in Phase 5 (Generate Solutions)"
        elif 51 <= step_num <= 60:
            return f"Step {step_num - 50} of 10 in Phase 6 (Rank & Implement)"
        return ""

    def _log_sources(
        self, tracker: TraceabilityLogger, findings: Dict[str, Any]
    ) -> List[str]:
        """Extract and log sources from findings"""
        source_ids = []

        # Look for common source patterns in findings
        if "sources" in findings and isinstance(findings["sources"], list):
            for source in findings["sources"]:
                if isinstance(source, dict):
                    source_id = tracker.add_source(
                        source_type=source.get("type", "unknown"),
                        source_name=source.get("name", "Unnamed source"),
                        content=source.get("content", ""),
                        relevance_score=source.get("score"),
                        metadata=source.get("metadata", {}),
                    )
                    source_ids.append(source_id)

        # Check for principle references
        if "principle_number" in findings:
            source_id = tracker.add_source(
                source_type="principle",
                source_name=f"TRIZ Principle {findings['principle_number']}",
                content=str(findings.get("principle_content", "")),
                metadata={"principle_number": findings["principle_number"]},
            )
            source_ids.append(source_id)

        # Check for material references
        if "material_name" in findings or "materials" in findings:
            materials = findings.get("materials", [findings.get("material_name")])
            for material in materials:
                if material:
                    source_id = tracker.add_source(
                        source_type="material",
                        source_name=str(material),
                        content=str(findings.get("material_properties", "")),
                        metadata=findings.get("material_metadata", {}),
                    )
                    source_ids.append(source_id)

        return source_ids

    def _log_findings(
        self,
        tracker: TraceabilityLogger,
        step_num: int,
        findings: Dict[str, Any],
        source_ids: List[str],
    ) -> List[str]:
        """Extract and log TRIZ findings"""
        finding_ids = []

        # Determine finding type based on step phase
        if 1 <= step_num <= 10:
            finding_type = "context_analysis"
        elif 11 <= step_num <= 16:
            finding_type = "ideal_definition"
        elif 17 <= step_num <= 26:
            finding_type = (
                "contradiction"
                if "contradiction" in str(findings).lower()
                else "function_analysis"
            )
        elif 27 <= step_num <= 32:
            finding_type = "tool_selection"
        elif 33 <= step_num <= 50:
            finding_type = (
                "solution"
                if "solution" in str(findings).lower()
                else "principle_application"
            )
        elif 51 <= step_num <= 60:
            finding_type = "evaluation"
        else:
            finding_type = "unknown"

        # Log the finding
        finding_id = tracker.add_finding(
            finding_type=finding_type,
            content=findings,
            source_ids=source_ids,
            step_number=step_num,
        )
        finding_ids.append(finding_id)

        return finding_ids

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
            "nine_boxes": session.nine_boxes,
            "current_ideality": session.current_ideality,
            "ideal_outcome": session.ideal_outcome,
            "function_map": session.function_map,
            "technical_contradictions": session.technical_contradictions,
            "physical_contradictions": session.physical_contradictions,
            "solution_concepts": session.solution_concepts,
            "steps": [
                {
                    "step_number": s.step_number,
                    "phase": s.phase.value,
                    "title": s.title,
                    "status": s.status.value,
                    "triz_tool": getattr(s, "triz_tool", ""),
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
                triz_tool=s.get("triz_tool", ""),
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
            nine_boxes=data.get("nine_boxes", {}),
            current_ideality=data.get("current_ideality", {}),
            ideal_outcome=data.get("ideal_outcome", {}),
            function_map=data.get("function_map", {}),
            technical_contradictions=data.get("technical_contradictions", []),
            physical_contradictions=data.get("physical_contradictions", []),
            solution_concepts=data.get("solution_concepts", []),
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
