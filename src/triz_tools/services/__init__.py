"""
TRIZ Services Module
Contains all service layer components including CLI subprocess execution
"""

from .vector_service import get_vector_service, VectorService
from .embedding_service import get_embedding_service, EmbeddingService
from .session_service import SessionService
from .analysis_service import get_analysis_service, TRIZAnalysisService
from .cli_executor import get_cli_executor, CLIExecutor, CLIResult
from .cli_config import get_cli_config, CLIConfig, is_cli_available
from .cli_prompts import get_prompt
from .research_persistence import (
    get_research_persistence,
    ResearchPersistence,
    list_research_sessions,
    load_session,
)

__all__ = [
    "get_vector_service",
    "VectorService",
    "get_embedding_service",
    "EmbeddingService",
    "SessionService",
    "get_analysis_service",
    "TRIZAnalysisService",
    "get_cli_executor",
    "CLIExecutor",
    "CLIResult",
    "get_cli_config",
    "CLIConfig",
    "is_cli_available",
    "get_prompt",
    "get_research_persistence",
    "ResearchPersistence",
    "list_research_sessions",
    "load_session",
]
