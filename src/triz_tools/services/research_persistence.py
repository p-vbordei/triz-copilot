"""
Research Persistence Service
Saves research findings to disk for context recovery and traceability
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

logger = logging.getLogger(__name__)

# Research storage directory
RESEARCH_DIR = Path.home() / ".triz_research"
RESEARCH_DIR.mkdir(exist_ok=True)


class ResearchPersistence:
    """
    Persists research findings to disk during analysis.
    Enables context recovery and full research traceability.
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize research persistence.

        Args:
            session_id: Session ID for grouping research (auto-generated if None)
        """
        self.session_id = session_id or self._generate_session_id()
        self.session_dir = RESEARCH_DIR / self.session_id
        self.session_dir.mkdir(exist_ok=True)

        # Create manifest file
        self.manifest_file = self.session_dir / "manifest.json"
        self.findings_file = self.session_dir / "findings.jsonl"
        self.subprocess_results_file = self.session_dir / "subprocess_results.jsonl"
        self.summary_file = self.session_dir / "summary.json"

        self._initialize_manifest()

        logger.info(f"Research persistence initialized: {self.session_dir}")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _initialize_manifest(self):
        """Initialize or load manifest"""
        if self.manifest_file.exists():
            with open(self.manifest_file, "r") as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {
                "session_id": self.session_id,
                "created_at": datetime.now().isoformat(),
                "problem_statement": None,
                "total_findings": 0,
                "total_subprocess_calls": 0,
                "research_queries": [],
                "last_updated": datetime.now().isoformat(),
            }
            self._save_manifest()

    def _save_manifest(self):
        """Save manifest to disk"""
        self.manifest["last_updated"] = datetime.now().isoformat()
        with open(self.manifest_file, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def set_problem(self, problem_statement: str):
        """
        Set the problem statement for this research session.

        Args:
            problem_statement: The problem being researched
        """
        self.manifest["problem_statement"] = problem_statement
        self._save_manifest()

    def save_research_query(self, query: Dict[str, Any]):
        """
        Save a research query that was executed.

        Args:
            query: Query metadata (query_text, query_type, priority, collections)
        """
        self.manifest["research_queries"].append(
            {
                "query": query.get("query_text"),
                "type": query.get("query_type"),
                "priority": query.get("priority"),
                "collections": query.get("target_collections", []),
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_manifest()

    def save_finding(self, finding: Dict[str, Any]):
        """
        Save a single research finding (append to JSONL).

        Args:
            finding: Finding data (source, content, relevance_score, metadata)
        """
        # Append to findings file (JSONL format for streaming)
        with open(self.findings_file, "a") as f:
            finding_record = {
                "timestamp": datetime.now().isoformat(),
                "source": finding.get("source"),
                "content": finding.get("content"),
                "relevance_score": finding.get("relevance_score"),
                "metadata": finding.get("metadata", {}),
                "citations": finding.get("citations", []),
            }
            f.write(json.dumps(finding_record) + "\n")

        self.manifest["total_findings"] += 1
        self._save_manifest()

    def save_findings_batch(self, findings: List[Dict[str, Any]]):
        """
        Save multiple findings at once.

        Args:
            findings: List of finding dicts
        """
        for finding in findings:
            self.save_finding(finding)

        logger.info(f"Saved {len(findings)} findings to {self.findings_file}")

    def save_subprocess_result(
        self,
        task_type: str,
        input_summary: str,
        result: Dict[str, Any],
        execution_time: float,
    ):
        """
        Save results from a subprocess execution.

        Args:
            task_type: Type of subprocess task
            input_summary: Summary of input (not full input to save space)
            result: Subprocess result data
            execution_time: Time taken for subprocess
        """
        with open(self.subprocess_results_file, "a") as f:
            record = {
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type,
                "input_summary": input_summary,
                "result": result,
                "execution_time": execution_time,
                "success": result.get("success", False),
            }
            f.write(json.dumps(record) + "\n")

        self.manifest["total_subprocess_calls"] += 1
        self._save_manifest()

        logger.info(f"Saved subprocess result: {task_type} ({execution_time:.2f}s)")

    def save_research_summary(
        self,
        contradictions: List[Dict[str, Any]],
        principles: List[Dict[str, Any]],
        solutions: List[Dict[str, Any]],
        confidence_score: float,
        knowledge_gaps: List[str],
    ):
        """
        Save final research summary.

        Args:
            contradictions: Identified contradictions
            principles: Relevant TRIZ principles
            solutions: Generated solutions
            confidence_score: Overall confidence
            knowledge_gaps: Identified gaps
        """
        summary = {
            "session_id": self.session_id,
            "problem_statement": self.manifest["problem_statement"],
            "total_findings": self.manifest["total_findings"],
            "total_subprocess_calls": self.manifest["total_subprocess_calls"],
            "contradictions": contradictions,
            "principles": principles,
            "solutions": solutions,
            "confidence_score": confidence_score,
            "knowledge_gaps": knowledge_gaps,
            "created_at": self.manifest["created_at"],
            "completed_at": datetime.now().isoformat(),
        }

        with open(self.summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Saved research summary to {self.summary_file}")

    def load_findings(self) -> List[Dict[str, Any]]:
        """
        Load all findings from disk.

        Returns:
            List of finding dicts
        """
        if not self.findings_file.exists():
            return []

        findings = []
        with open(self.findings_file, "r") as f:
            for line in f:
                findings.append(json.loads(line))

        return findings

    def load_subprocess_results(self) -> List[Dict[str, Any]]:
        """
        Load all subprocess results from disk.

        Returns:
            List of subprocess result dicts
        """
        if not self.subprocess_results_file.exists():
            return []

        results = []
        with open(self.subprocess_results_file, "r") as f:
            for line in f:
                results.append(json.loads(line))

        return results

    def load_summary(self) -> Optional[Dict[str, Any]]:
        """
        Load research summary.

        Returns:
            Summary dict or None if not found
        """
        if not self.summary_file.exists():
            return None

        with open(self.summary_file, "r") as f:
            return json.load(f)

    def get_session_path(self) -> Path:
        """Get the session directory path"""
        return self.session_dir

    def get_research_stats(self) -> Dict[str, Any]:
        """
        Get statistics about this research session.

        Returns:
            Dict with stats
        """
        findings = self.load_findings()
        subprocess_results = self.load_subprocess_results()

        # Calculate subprocess stats
        subprocess_total_time = sum(
            r.get("execution_time", 0) for r in subprocess_results
        )
        subprocess_success_rate = (
            sum(1 for r in subprocess_results if r.get("success", False))
            / len(subprocess_results)
            if subprocess_results
            else 0
        )

        # Calculate finding stats
        avg_relevance = (
            sum(f.get("relevance_score", 0) for f in findings) / len(findings)
            if findings
            else 0
        )

        # Get unique sources
        sources = set(f.get("source") for f in findings)

        return {
            "session_id": self.session_id,
            "session_path": str(self.session_dir),
            "total_findings": len(findings),
            "total_subprocess_calls": len(subprocess_results),
            "subprocess_total_time": subprocess_total_time,
            "subprocess_success_rate": subprocess_success_rate,
            "average_relevance": avg_relevance,
            "unique_sources": len(sources),
            "sources": list(sources),
            "created_at": self.manifest.get("created_at"),
            "last_updated": self.manifest.get("last_updated"),
        }

    def create_recovery_file(self) -> Path:
        """
        Create a markdown recovery file for easy viewing.

        Returns:
            Path to recovery file
        """
        recovery_file = self.session_dir / "RECOVERY.md"

        findings = self.load_findings()
        subprocess_results = self.load_subprocess_results()
        summary = self.load_summary()
        stats = self.get_research_stats()

        with open(recovery_file, "w") as f:
            f.write(f"# Research Session Recovery\n\n")
            f.write(f"**Session ID**: `{self.session_id}`\n")
            f.write(
                f"**Created**: {self.manifest.get('created_at', 'Unknown')}\n\n"
            )

            # Problem
            f.write(f"## Problem Statement\n\n")
            f.write(
                f"{self.manifest.get('problem_statement', 'Not recorded')}\n\n"
            )

            # Stats
            f.write(f"## Research Statistics\n\n")
            f.write(f"- Total Findings: {stats['total_findings']}\n")
            f.write(f"- Subprocess Calls: {stats['total_subprocess_calls']}\n")
            f.write(
                f"- Subprocess Time: {stats['subprocess_total_time']:.2f}s\n"
            )
            f.write(
                f"- Success Rate: {stats['subprocess_success_rate']*100:.1f}%\n"
            )
            f.write(f"- Unique Sources: {stats['unique_sources']}\n")
            f.write(f"- Average Relevance: {stats['average_relevance']:.3f}\n\n")

            # Research queries
            f.write(f"## Research Queries Executed\n\n")
            for i, query in enumerate(self.manifest.get("research_queries", []), 1):
                f.write(f"{i}. **{query.get('type')}**: {query.get('query')}\n")
                f.write(
                    f"   - Priority: {query.get('priority')}, Collections: {', '.join(query.get('collections', []))}\n"
                )
            f.write("\n")

            # Subprocess results summary
            f.write(f"## Subprocess Analysis Results\n\n")
            for i, result in enumerate(subprocess_results, 1):
                f.write(
                    f"### {i}. {result.get('task_type')} "
                    f"({result.get('execution_time', 0):.2f}s)\n\n"
                )
                f.write(f"**Status**: {'✅ Success' if result.get('success') else '❌ Failed'}\n")
                f.write(f"**Input**: {result.get('input_summary', 'N/A')}\n\n")

                # Show result preview
                if result.get("result"):
                    f.write(f"**Result Preview**:\n```json\n")
                    f.write(
                        json.dumps(result["result"], indent=2)[:500] + "...\n"
                    )
                    f.write(f"```\n\n")

            # Summary
            if summary:
                f.write(f"## Final Summary\n\n")
                f.write(
                    f"**Confidence Score**: {summary.get('confidence_score', 0):.2f}\n\n"
                )

                f.write(f"### Contradictions ({len(summary.get('contradictions', []))})\n\n")
                for c in summary.get("contradictions", [])[:5]:
                    f.write(
                        f"- {c.get('improving', 'N/A')} vs {c.get('worsening', 'N/A')}\n"
                    )
                f.write("\n")

                f.write(f"### Top Principles ({len(summary.get('principles', []))})\n\n")
                for p in summary.get("principles", [])[:5]:
                    f.write(f"- **P{p.get('id')}**: {p.get('name')} (score: {p.get('score', 0):.2f})\n")
                f.write("\n")

                f.write(f"### Solutions ({len(summary.get('solutions', []))})\n\n")
                for i, s in enumerate(summary.get("solutions", []), 1):
                    f.write(f"{i}. **{s.get('title')}**\n")
                    f.write(f"   - Feasibility: {s.get('feasibility_score', 0):.2f}\n")
                    f.write(
                        f"   - {s.get('description', 'No description')[:200]}...\n\n"
                    )

            # Data files reference
            f.write(f"## Data Files\n\n")
            f.write(f"- Manifest: `{self.manifest_file.name}`\n")
            f.write(
                f"- Findings (JSONL): `{self.findings_file.name}` ({stats['total_findings']} entries)\n"
            )
            f.write(
                f"- Subprocess Results: `{self.subprocess_results_file.name}` ({stats['total_subprocess_calls']} entries)\n"
            )
            f.write(f"- Summary: `{self.summary_file.name}`\n\n")

            f.write(f"---\n\n")
            f.write(
                f"*Research session: {self.session_dir}*\n"
            )

        logger.info(f"Created recovery file: {recovery_file}")
        return recovery_file


# Singleton for current session
_current_persistence: Optional[ResearchPersistence] = None


def get_research_persistence(
    session_id: Optional[str] = None, reset: bool = False
) -> ResearchPersistence:
    """
    Get or create research persistence singleton.

    Args:
        session_id: Session ID (auto-generated if None)
        reset: Force create new persistence

    Returns:
        ResearchPersistence instance
    """
    global _current_persistence

    if reset or _current_persistence is None:
        _current_persistence = ResearchPersistence(session_id=session_id)

    return _current_persistence


def list_research_sessions() -> List[Dict[str, Any]]:
    """
    List all research sessions on disk.

    Returns:
        List of session info dicts
    """
    sessions = []

    for session_dir in RESEARCH_DIR.iterdir():
        if not session_dir.is_dir():
            continue

        manifest_file = session_dir / "manifest.json"
        if not manifest_file.exists():
            continue

        with open(manifest_file, "r") as f:
            manifest = json.load(f)

        sessions.append(
            {
                "session_id": manifest.get("session_id"),
                "path": str(session_dir),
                "problem": manifest.get("problem_statement"),
                "total_findings": manifest.get("total_findings", 0),
                "created_at": manifest.get("created_at"),
                "last_updated": manifest.get("last_updated"),
            }
        )

    # Sort by last updated
    sessions.sort(key=lambda x: x.get("last_updated", ""), reverse=True)

    return sessions


def load_session(session_id: str) -> Optional[ResearchPersistence]:
    """
    Load an existing research session.

    Args:
        session_id: Session ID to load

    Returns:
        ResearchPersistence instance or None if not found
    """
    session_dir = RESEARCH_DIR / session_id

    if not session_dir.exists():
        return None

    return ResearchPersistence(session_id=session_id)
