"""
CLI Subprocess Configuration
Detects and configures available AI CLI tools (Claude, Gemini)
"""

import os
import subprocess
import logging
from typing import Optional, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

CLIModel = Literal["claude", "gemini", "auto"]


@dataclass
class CLIConfig:
    """Configuration for CLI subprocess execution"""

    model: str  # "claude" or "gemini"
    command: list[str]  # Full command to execute
    available: bool
    max_tokens: int = 4000
    timeout: int = 60
    max_parallel: int = 5


def detect_available_cli() -> Optional[str]:
    """
    Detect which AI CLI is available on the system.

    Returns:
        "claude", "gemini", or None if neither available
    """
    # Try Claude first
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            logger.info("Detected Claude CLI")
            return "claude"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try Gemini
    try:
        result = subprocess.run(
            ["gemini", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            logger.info("Detected Gemini CLI")
            return "gemini"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    logger.warning("No AI CLI detected (neither claude nor gemini)")
    return None


def get_cli_config(model: CLIModel = "auto") -> Optional[CLIConfig]:
    """
    Get CLI configuration based on model preference.

    Args:
        model: "claude", "gemini", or "auto" for auto-detection

    Returns:
        CLIConfig or None if CLI not available
    """
    # Get from environment or use parameter
    preferred_model = os.getenv("TRIZ_CLI_MODEL", model)
    timeout = int(os.getenv("TRIZ_CLI_TIMEOUT", "60"))
    max_parallel = int(os.getenv("TRIZ_CLI_MAX_PARALLEL", "5"))

    # Auto-detect if needed
    if preferred_model == "auto":
        detected = detect_available_cli()
        if not detected:
            return None
        preferred_model = detected

    # Build configuration for detected model
    if preferred_model == "claude":
        # Try to detect if claude is available
        try:
            subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=5,
            )
            return CLIConfig(
                model="claude",
                command=["claude", "chat", "--no-stream"],
                available=True,
                timeout=timeout,
                max_parallel=max_parallel,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Claude CLI requested but not available")
            return None

    elif preferred_model == "gemini":
        try:
            subprocess.run(
                ["gemini", "--version"],
                capture_output=True,
                timeout=5,
            )
            return CLIConfig(
                model="gemini",
                command=["gemini", "chat"],
                available=True,
                timeout=timeout,
                max_parallel=max_parallel,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Gemini CLI requested but not available")
            return None

    return None


def is_cli_available() -> bool:
    """Check if any AI CLI is available"""
    return detect_available_cli() is not None
