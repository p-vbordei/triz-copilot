"""
Session Manager with JSON Persistence (T035)
Manages TRIZ workflow sessions with file-based persistence.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from .services.session_service import (
    get_session_service,
    SessionData,
    SessionStage
)

logger = logging.getLogger(__name__)


class SessionManager:
    """High-level session management interface"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize session manager.
        
        Args:
            storage_dir: Directory for session storage
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".triz_copilot" / "sessions"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Use session service for heavy lifting
        self.service = get_session_service(storage_dir=storage_dir)
        
        logger.info(f"Session manager initialized at {self.storage_dir}")
    
    def create_session(self) -> str:
        """
        Create a new TRIZ workflow session.
        
        Returns:
            Session ID
        """
        session = self.service.create_session({
            "created_via": "session_manager",
            "timestamp": datetime.now().isoformat()
        })
        
        return session.session_id
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data dictionary or None
        """
        session = self.service.get_session(session_id)
        
        if session:
            return session.to_dict()
        
        return None
    
    def update_session(
        self,
        session_id: str,
        stage: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update session with new data.
        
        Args:
            session_id: Session ID
            stage: New stage name
            data: Data to update
        
        Returns:
            True if successful
        """
        updates = data or {}
        
        # Convert stage string to enum if provided
        advance_stage = False
        if stage:
            try:
                new_stage = SessionStage(stage)
                updates["stage"] = new_stage
            except ValueError:
                # Try to advance to next stage
                advance_stage = True
        
        session = self.service.update_session(
            session_id,
            updates,
            advance_stage=advance_stage
        )
        
        return session is not None
    
    def save_problem_statement(
        self,
        session_id: str,
        problem: str
    ) -> bool:
        """
        Save problem statement to session.
        
        Args:
            session_id: Session ID
            problem: Problem statement
        
        Returns:
            True if successful
        """
        return self.update_session(
            session_id,
            data={"problem_statement": problem}
        )
    
    def save_ideal_final_result(
        self,
        session_id: str,
        ifr: str
    ) -> bool:
        """
        Save IFR to session.
        
        Args:
            session_id: Session ID
            ifr: Ideal final result
        
        Returns:
            True if successful
        """
        return self.update_session(
            session_id,
            data={"ideal_final_result": ifr}
        )
    
    def save_contradictions(
        self,
        session_id: str,
        contradictions: list
    ) -> bool:
        """
        Save contradictions to session.
        
        Args:
            session_id: Session ID
            contradictions: List of contradictions
        
        Returns:
            True if successful
        """
        return self.update_session(
            session_id,
            data={"contradictions": contradictions}
        )
    
    def save_selected_principles(
        self,
        session_id: str,
        principles: list
    ) -> bool:
        """
        Save selected principles to session.
        
        Args:
            session_id: Session ID
            principles: List of principle IDs
        
        Returns:
            True if successful
        """
        return self.update_session(
            session_id,
            data={"selected_principles": principles}
        )
    
    def save_solution_concepts(
        self,
        session_id: str,
        concepts: list
    ) -> bool:
        """
        Save solution concepts to session.
        
        Args:
            session_id: Session ID
            concepts: List of solution concepts
        
        Returns:
            True if successful
        """
        return self.update_session(
            session_id,
            data={"solution_concepts": concepts}
        )
    
    def get_current_stage(self, session_id: str) -> Optional[str]:
        """
        Get current workflow stage.
        
        Args:
            session_id: Session ID
        
        Returns:
            Stage name or None
        """
        session = self.service.get_session(session_id)
        
        if session:
            return session.stage.value
        
        return None
    
    def advance_stage(self, session_id: str) -> Optional[str]:
        """
        Advance to next workflow stage.
        
        Args:
            session_id: Session ID
        
        Returns:
            New stage name or None
        """
        session = self.service.update_session(
            session_id,
            {},
            advance_stage=True
        )
        
        if session:
            return session.stage.value
        
        return None
    
    def reset_session(self, session_id: str) -> bool:
        """
        Reset session to initial state.
        
        Args:
            session_id: Session ID
        
        Returns:
            True if successful
        """
        return self.update_session(
            session_id,
            stage="problem_definition",
            data={
                "problem_statement": None,
                "ideal_final_result": None,
                "contradictions": [],
                "selected_principles": [],
                "solution_concepts": [],
                "evaluation_results": None
            }
        )
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            True if deleted
        """
        return self.service.delete_session(session_id)
    
    def list_sessions(self, limit: int = 10) -> list:
        """
        List recent sessions.
        
        Args:
            limit: Maximum sessions to return
        
        Returns:
            List of session summaries
        """
        sessions = self.service.list_sessions(limit=limit)
        
        summaries = []
        for session in sessions:
            summaries.append({
                "session_id": session.session_id,
                "stage": session.stage.value,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "has_problem": session.problem_statement is not None,
                "has_solutions": len(session.solution_concepts) > 0
            })
        
        return summaries
    
    def export_session(
        self,
        session_id: str,
        output_file: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Export session to JSON file.
        
        Args:
            session_id: Session ID
            output_file: Output file path
        
        Returns:
            Path to exported file or None
        """
        session = self.service.get_session(session_id)
        
        if not session:
            logger.warning(f"Session {session_id} not found")
            return None
        
        if output_file is None:
            output_file = Path(f"triz_session_{session_id}.json")
        
        try:
            with open(output_file, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
            
            logger.info(f"Exported session to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to export session: {str(e)}")
            return None
    
    def import_session(
        self,
        input_file: Path
    ) -> Optional[str]:
        """
        Import session from JSON file.
        
        Args:
            input_file: Input file path
        
        Returns:
            Imported session ID or None
        """
        if not input_file.exists():
            logger.warning(f"Import file not found: {input_file}")
            return None
        
        try:
            with open(input_file, "r") as f:
                data = json.load(f)
            
            # Create new session with imported data
            session = SessionData.from_dict(data)
            
            # Generate new ID to avoid conflicts
            session.session_id = str(uuid4())
            session.metadata["imported_from"] = str(input_file)
            session.metadata["imported_at"] = datetime.now().isoformat()
            
            # Save using service
            self.service._save_session(session)
            
            logger.info(f"Imported session as {session.session_id}")
            return session.session_id
            
        except Exception as e:
            logger.error(f"Failed to import session: {str(e)}")
            return None
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Clean up old sessions.
        
        Args:
            days: Delete sessions older than this
        
        Returns:
            Number of sessions deleted
        """
        return self.service.cleanup_old_sessions(days=days)


# Convenience functions for direct access
_default_manager: Optional[SessionManager] = None


def get_session_manager(
    storage_dir: Optional[Path] = None,
    reset: bool = False
) -> SessionManager:
    """Get or create default session manager"""
    global _default_manager
    
    if reset or _default_manager is None:
        _default_manager = SessionManager(storage_dir=storage_dir)
    
    return _default_manager


def create_session() -> str:
    """Create a new session using default manager"""
    manager = get_session_manager()
    return manager.create_session()


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data using default manager"""
    manager = get_session_manager()
    return manager.get_session_data(session_id)


def update_session(
    session_id: str,
    stage: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """Update session using default manager"""
    manager = get_session_manager()
    return manager.update_session(session_id, stage, data)


def delete_session(session_id: str) -> bool:
    """Delete session using default manager"""
    manager = get_session_manager()
    return manager.delete_session(session_id)


def list_sessions(limit: int = 10) -> list:
    """List sessions using default manager"""
    manager = get_session_manager()
    return manager.list_sessions(limit=limit)