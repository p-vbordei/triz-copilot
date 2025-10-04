"""
Traceability Logger for TRIZ Sessions
Provides comprehensive documentation of all TRIZ analysis with full source tracing.
Every finding, source, and step is indexed for complete know-how reconstruction.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


@dataclass
class SourceCitation:
    """A single source citation with full traceability"""

    source_id: str  # Unique ID for this source
    source_type: str  # "principle", "material", "book_chunk", "matrix", etc.
    source_name: str  # Name/title of the source
    content: str  # The actual content referenced
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TRIZFinding:
    """A TRIZ finding with source traceability"""

    finding_id: str
    finding_type: str  # "contradiction", "principle", "solution", "material", etc.
    content: Dict[str, Any]  # The actual finding data
    source_citations: List[str]  # List of source_ids that led to this finding
    step_number: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class StepRecord:
    """Record of a single workflow step"""

    step_number: int
    step_name: str
    user_input: str
    system_response: str
    findings_generated: List[str]  # List of finding_ids
    sources_used: List[str]  # List of source_ids
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TraceabilityLogger:
    """
    Comprehensive logging system for TRIZ sessions.
    Ensures complete traceability from problem to solution.
    """

    def __init__(self, session_id: str, base_dir: Optional[Path] = None):
        """
        Initialize traceability logger for a session.

        Args:
            session_id: The TRIZ session ID
            base_dir: Base directory for logs (default: ~/.triz_copilot/sessions)
        """
        if base_dir is None:
            base_dir = Path.home() / ".triz_copilot" / "sessions"

        self.session_id = session_id
        self.session_dir = base_dir / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize storage structures
        self.sources: Dict[str, SourceCitation] = {}
        self.findings: Dict[str, TRIZFinding] = {}
        self.steps: List[StepRecord] = []

        # File paths
        self.manifest_file = self.session_dir / "session_manifest.json"
        self.findings_file = self.session_dir / "triz_findings.json"
        self.sources_file = self.session_dir / "sources.json"
        self.steps_file = self.session_dir / "step_log.json"
        self.materials_file = self.session_dir / "materials_research.json"
        self.solution_file = self.session_dir / "final_solution.md"

        # Initialize manifest
        self.manifest = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "problem_statement": "",
            "current_step": 0,
            "total_steps": 60,
            "status": "active",
            "statistics": {
                "total_sources": 0,
                "total_findings": 0,
                "total_steps_completed": 0,
            },
        }

        self._save_manifest()
        logger.info(f"Traceability logger initialized for session {session_id}")

    def log_problem(self, problem: str) -> None:
        """Log the initial problem statement"""
        self.manifest["problem_statement"] = problem
        self.manifest["last_updated"] = datetime.now().isoformat()
        self._save_manifest()
        logger.info(f"Problem logged: {problem[:100]}...")

    def add_source(
        self,
        source_type: str,
        source_name: str,
        content: str,
        relevance_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a source citation.

        Args:
            source_type: Type of source (principle, book, matrix, etc.)
            source_name: Name/title of the source
            content: The actual content
            relevance_score: Optional relevance score
            metadata: Additional metadata

        Returns:
            source_id for referencing this source
        """
        source_id = f"SRC-{len(self.sources) + 1:04d}"

        citation = SourceCitation(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            content=content,
            relevance_score=relevance_score,
            metadata=metadata or {},
        )

        self.sources[source_id] = citation
        self.manifest["statistics"]["total_sources"] = len(self.sources)
        self.manifest["last_updated"] = datetime.now().isoformat()

        self._save_sources()
        self._save_manifest()

        logger.debug(f"Added source {source_id}: {source_name}")
        return source_id

    def add_finding(
        self,
        finding_type: str,
        content: Dict[str, Any],
        source_ids: List[str],
        step_number: Optional[int] = None,
    ) -> str:
        """
        Add a TRIZ finding with source citations.

        Args:
            finding_type: Type of finding (contradiction, principle, solution, etc.)
            content: The finding data
            source_ids: List of source IDs that support this finding
            step_number: Optional step number

        Returns:
            finding_id for referencing this finding
        """
        finding_id = f"FIND-{len(self.findings) + 1:04d}"

        finding = TRIZFinding(
            finding_id=finding_id,
            finding_type=finding_type,
            content=content,
            source_citations=source_ids,
            step_number=step_number,
        )

        self.findings[finding_id] = finding
        self.manifest["statistics"]["total_findings"] = len(self.findings)
        self.manifest["last_updated"] = datetime.now().isoformat()

        self._save_findings()
        self._save_manifest()

        logger.debug(f"Added finding {finding_id}: {finding_type}")
        return finding_id

    def log_step(
        self,
        step_number: int,
        step_name: str,
        user_input: str,
        system_response: str,
        findings_generated: Optional[List[str]] = None,
        sources_used: Optional[List[str]] = None,
    ) -> None:
        """
        Log a workflow step.

        Args:
            step_number: Step number (1-60)
            step_name: Name of the step
            user_input: User's input for this step
            system_response: System's response
            findings_generated: List of finding IDs generated
            sources_used: List of source IDs used
        """
        step_record = StepRecord(
            step_number=step_number,
            step_name=step_name,
            user_input=user_input,
            system_response=system_response,
            findings_generated=findings_generated or [],
            sources_used=sources_used or [],
        )

        self.steps.append(step_record)
        self.manifest["current_step"] = step_number
        self.manifest["statistics"]["total_steps_completed"] = len(self.steps)
        self.manifest["last_updated"] = datetime.now().isoformat()

        self._save_steps()
        self._save_manifest()

        logger.info(f"Logged step {step_number}: {step_name}")

    def log_materials_research(
        self, materials_data: Dict[str, Any], source_ids: List[str]
    ) -> None:
        """
        Log materials research with sources.

        Args:
            materials_data: Materials research data
            source_ids: Source IDs for this research
        """
        research_record = {
            "timestamp": datetime.now().isoformat(),
            "materials": materials_data,
            "sources": source_ids,
            "session_id": self.session_id,
        }

        with open(self.materials_file, "w") as f:
            json.dump(research_record, f, indent=2)

        logger.info(f"Materials research logged with {len(source_ids)} sources")

    def generate_final_solution(self, solution_data: Dict[str, Any]) -> Path:
        """
        Generate final solution document with complete traceability.

        Args:
            solution_data: Complete solution data

        Returns:
            Path to solution markdown file
        """
        # Build solution markdown with citations
        md_content = f"""# TRIZ Solution: {self.manifest["problem_statement"]}

**Session ID:** {self.session_id}
**Generated:** {datetime.now().isoformat()}
**Total Steps:** {len(self.steps)}
**Sources Consulted:** {len(self.sources)}

---

## Problem Statement

{self.manifest["problem_statement"]}

---

## Solution Overview

"""

        # Add solutions with traceability
        solutions = [f for f in self.findings.values() if f.finding_type == "solution"]

        for i, solution in enumerate(solutions, 1):
            md_content += f"\n### Solution {i}\n\n"
            md_content += f"{solution.content.get('description', 'No description')}\n\n"

            # Add source citations
            md_content += "**Sources:**\n"
            for src_id in solution.source_citations:
                if src_id in self.sources:
                    src = self.sources[src_id]
                    md_content += f"- [{src_id}] {src.source_type}: {src.source_name}\n"
            md_content += "\n"

        # Add contradictions section
        contradictions = [
            f for f in self.findings.values() if f.finding_type == "contradiction"
        ]
        if contradictions:
            md_content += "\n---\n\n## Contradictions Identified\n\n"
            for contradiction in contradictions:
                md_content += f"- {contradiction.content.get('description', '')}\n"

        # Add principles used
        principles = [
            f for f in self.findings.values() if f.finding_type == "principle"
        ]
        if principles:
            md_content += "\n---\n\n## TRIZ Principles Applied\n\n"
            for principle in principles:
                md_content += f"- **Principle {principle.content.get('number', '')}**: {principle.content.get('name', '')}\n"

        # Add materials research if available
        if self.materials_file.exists():
            md_content += "\n---\n\n## Materials Research\n\n"
            md_content += (
                "See `materials_research.json` for detailed materials analysis.\n"
            )

        # Add complete source index
        md_content += "\n---\n\n## Source Index\n\n"
        md_content += "Complete traceability of all sources used:\n\n"

        for src_id, src in self.sources.items():
            md_content += f"### {src_id}\n"
            md_content += f"- **Type:** {src.source_type}\n"
            md_content += f"- **Name:** {src.source_name}\n"
            if src.relevance_score:
                md_content += f"- **Relevance:** {src.relevance_score:.2f}\n"
            md_content += f"- **Content:** {src.content[:200]}...\n\n"

        # Add step-by-step trace
        md_content += "\n---\n\n## Step-by-Step Trace\n\n"
        md_content += "Complete workflow progression:\n\n"

        for step in self.steps:
            md_content += f"### Step {step.step_number}: {step.step_name}\n"
            md_content += f"- **User Input:** {step.user_input[:100]}...\n"
            md_content += f"- **Findings Generated:** {len(step.findings_generated)}\n"
            md_content += f"- **Sources Used:** {len(step.sources_used)}\n\n"

        # Save markdown
        with open(self.solution_file, "w") as f:
            f.write(md_content)

        self.manifest["status"] = "completed"
        self.manifest["completed_at"] = datetime.now().isoformat()
        self._save_manifest()

        logger.info(f"Final solution generated: {self.solution_file}")
        return self.solution_file

    def _save_manifest(self) -> None:
        """Save session manifest"""
        with open(self.manifest_file, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def _save_sources(self) -> None:
        """Save sources index"""
        sources_dict = {sid: asdict(src) for sid, src in self.sources.items()}
        with open(self.sources_file, "w") as f:
            json.dump(sources_dict, f, indent=2)

    def _save_findings(self) -> None:
        """Save findings index"""
        findings_dict = {fid: asdict(finding) for fid, finding in self.findings.items()}
        with open(self.findings_file, "w") as f:
            json.dump(findings_dict, f, indent=2)

    def _save_steps(self) -> None:
        """Save step log"""
        steps_list = [asdict(step) for step in self.steps]
        with open(self.steps_file, "w") as f:
            json.dump(steps_list, f, indent=2)

    @classmethod
    def load_session(
        cls, session_id: str, base_dir: Optional[Path] = None
    ) -> "TraceabilityLogger":
        """
        Load an existing session for continuation.

        Args:
            session_id: Session ID to load
            base_dir: Base directory for sessions

        Returns:
            Loaded TraceabilityLogger instance
        """
        logger_instance = cls(session_id, base_dir)

        # Load existing data
        if logger_instance.manifest_file.exists():
            with open(logger_instance.manifest_file) as f:
                logger_instance.manifest = json.load(f)

        if logger_instance.sources_file.exists():
            with open(logger_instance.sources_file) as f:
                sources_data = json.load(f)
                logger_instance.sources = {
                    sid: SourceCitation(**data) for sid, data in sources_data.items()
                }

        if logger_instance.findings_file.exists():
            with open(logger_instance.findings_file) as f:
                findings_data = json.load(f)
                logger_instance.findings = {
                    fid: TRIZFinding(**data) for fid, data in findings_data.items()
                }

        if logger_instance.steps_file.exists():
            with open(logger_instance.steps_file) as f:
                steps_data = json.load(f)
                logger_instance.steps = [StepRecord(**step) for step in steps_data]

        logger.info(
            f"Loaded session {session_id} with {len(logger_instance.steps)} steps"
        )
        return logger_instance

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session state"""
        return {
            "session_id": self.session_id,
            "problem": self.manifest.get("problem_statement", ""),
            "current_step": self.manifest.get("current_step", 0),
            "status": self.manifest.get("status", "active"),
            "statistics": self.manifest.get("statistics", {}),
            "session_dir": str(self.session_dir),
            "files": {
                "manifest": str(self.manifest_file),
                "findings": str(self.findings_file),
                "sources": str(self.sources_file),
                "steps": str(self.steps_file),
                "materials": str(self.materials_file)
                if self.materials_file.exists()
                else None,
                "solution": str(self.solution_file)
                if self.solution_file.exists()
                else None,
            },
        }
