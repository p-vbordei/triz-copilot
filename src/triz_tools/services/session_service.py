"""
Session Management Service (T030)
Manages TRIZ workflow sessions with persistence.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStage(Enum):
    """TRIZ workflow stages"""
    PROBLEM_DEFINITION = "problem_definition"
    IDEAL_FINAL_RESULT = "ideal_final_result"
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    PRINCIPLE_SELECTION = "principle_selection"
    SOLUTION_GENERATION = "solution_generation"
    EVALUATION = "evaluation"
    COMPLETED = "completed"


@dataclass
class SessionData:
    """Session data structure"""
    session_id: str
    stage: SessionStage
    created_at: str
    updated_at: str
    problem_statement: Optional[str] = None
    ideal_final_result: Optional[str] = None
    contradictions: List[Dict[str, Any]] = None
    selected_principles: List[int] = None
    solution_concepts: List[Dict[str, Any]] = None
    evaluation_results: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.contradictions is None:
            self.contradictions = []
        if self.selected_principles is None:
            self.selected_principles = []
        if self.solution_concepts is None:
            self.solution_concepts = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['stage'] = self.stage.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create from dictionary"""
        data = data.copy()
        if 'stage' in data and isinstance(data['stage'], str):
            data['stage'] = SessionStage(data['stage'])
        return cls(**data)


class SessionService:
    """Service for managing TRIZ workflow sessions"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize session service.
        
        Args:
            storage_dir: Directory for storing sessions
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".triz_copilot" / "sessions"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._sessions: Dict[str, SessionData] = {}
        self._load_recent_sessions()
        
        logger.info(f"Session service initialized at {self.storage_dir}")
    
    def _load_recent_sessions(self, max_age_days: int = 7):
        """Load recent sessions into cache"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        for session_file in self.storage_dir.glob("*.json"):
            try:
                # Check file age
                file_time = datetime.fromtimestamp(session_file.stat().st_mtime)
                if file_time < cutoff_date:
                    continue
                
                # Load session
                with open(session_file, "r") as f:
                    data = json.load(f)
                    session = SessionData.from_dict(data)
                    self._sessions[session.session_id] = session
                    
            except Exception as e:
                logger.warning(f"Failed to load session {session_file.name}: {str(e)}")
        
        logger.info(f"Loaded {len(self._sessions)} recent sessions")
    
    def _save_session(self, session: SessionData):
        """Save session to disk"""
        session_file = self.storage_dir / f"{session.session_id}.json"
        
        # Update timestamp
        session.updated_at = datetime.now().isoformat()
        
        # Save to file
        with open(session_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
        
        # Update cache
        self._sessions[session.session_id] = session
    
    def create_session(self, initial_data: Optional[Dict[str, Any]] = None) -> SessionData:
        """
        Create a new session.
        
        Args:
            initial_data: Optional initial session data
        
        Returns:
            New session object
        """
        session_id = str(uuid4())
        now = datetime.now().isoformat()
        
        session = SessionData(
            session_id=session_id,
            stage=SessionStage.PROBLEM_DEFINITION,
            created_at=now,
            updated_at=now,
            metadata=initial_data or {}
        )
        
        self._save_session(session)
        logger.info(f"Created session {session_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session object or None
        """
        # Check cache first
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # Try loading from disk
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    session = SessionData.from_dict(data)
                    self._sessions[session_id] = session
                    return session
            except Exception as e:
                logger.error(f"Failed to load session {session_id}: {str(e)}")
        
        return None
    
    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
        advance_stage: bool = False
    ) -> Optional[SessionData]:
        """
        Update session data.
        
        Args:
            session_id: Session ID
            updates: Data to update
            advance_stage: Whether to advance to next stage
        
        Returns:
            Updated session or None
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
            else:
                # Store in metadata
                session.metadata[key] = value
        
        # Advance stage if requested
        if advance_stage:
            next_stage = self._get_next_stage(session.stage)
            if next_stage:
                session.stage = next_stage
                logger.info(f"Advanced session {session_id} to {next_stage.value}")
        
        # Save changes
        self._save_session(session)
        
        return session
    
    def _get_next_stage(self, current_stage: SessionStage) -> Optional[SessionStage]:
        """Get the next workflow stage"""
        stage_order = [
            SessionStage.PROBLEM_DEFINITION,
            SessionStage.IDEAL_FINAL_RESULT,
            SessionStage.CONTRADICTION_ANALYSIS,
            SessionStage.PRINCIPLE_SELECTION,
            SessionStage.SOLUTION_GENERATION,
            SessionStage.EVALUATION,
            SessionStage.COMPLETED
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            True if deleted
        """
        # Remove from cache
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        # Delete file
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            logger.info(f"Deleted session {session_id}")
            return True
        
        return False
    
    def list_sessions(
        self,
        limit: int = 10,
        stage_filter: Optional[SessionStage] = None
    ) -> List[SessionData]:
        """
        List sessions.
        
        Args:
            limit: Maximum sessions to return
            stage_filter: Filter by stage
        
        Returns:
            List of sessions
        """
        sessions = list(self._sessions.values())
        
        # Apply filter
        if stage_filter:
            sessions = [s for s in sessions if s.stage == stage_filter]
        
        # Sort by update time (newest first)
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        return sessions[:limit]
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Clean up old sessions.
        
        Args:
            days: Delete sessions older than this
        
        Returns:
            Number of sessions deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for session_file in self.storage_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(session_file.stat().st_mtime)
                if file_time < cutoff_date:
                    session_id = session_file.stem
                    if self.delete_session(session_id):
                        deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to check session file {session_file}: {str(e)}")
        
        logger.info(f"Cleaned up {deleted_count} old sessions")
        return deleted_count
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics about sessions"""
        total = len(self._sessions)
        
        stage_counts = {}
        for session in self._sessions.values():
            stage_name = session.stage.value
            stage_counts[stage_name] = stage_counts.get(stage_name, 0) + 1
        
        return {
            "total_sessions": total,
            "stage_distribution": stage_counts,
            "storage_location": str(self.storage_dir),
            "cache_size": total
        }


# Singleton instance
_session_service: Optional[SessionService] = None


def get_session_service(
    storage_dir: Optional[Path] = None,
    reset: bool = False
) -> SessionService:
    """
    Get or create session service singleton.
    
    Args:
        storage_dir: Storage directory
        reset: Force create new instance
    
    Returns:
        SessionService instance
    """
    global _session_service
    
    if reset or _session_service is None:
        _session_service = SessionService(storage_dir=storage_dir)
    
    return _session_service