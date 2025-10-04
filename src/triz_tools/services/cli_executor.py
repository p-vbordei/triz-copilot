"""
CLI Subprocess Executor
Executes AI CLI commands as subprocesses to offload heavy analysis
Uses Unix-style stdin piping for context compression
"""

import subprocess
import json
import logging
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .cli_config import get_cli_config, CLIConfig, CLIModel
from .cli_prompts import get_prompt

logger = logging.getLogger(__name__)


@dataclass
class CLIResult:
    """Result from CLI subprocess execution"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    raw_output: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0


class CLIExecutor:
    """
    Executes AI CLI commands as subprocesses.

    This allows offloading heavy analysis (e.g., 500 research findings)
    to a subprocess that returns concise JSON summaries.
    """

    def __init__(self, model: CLIModel = "auto"):
        """
        Initialize CLI executor.

        Args:
            model: CLI model to use ("claude", "gemini", or "auto")
        """
        self.config = get_cli_config(model)
        self.available = self.config is not None

        if not self.available:
            logger.warning("CLI subprocess not available - will use fallback methods")
        else:
            logger.info(f"CLI executor initialized with {self.config.model}")

    def execute(
        self,
        task_type: str,
        timeout: Optional[int] = None,
        **template_vars,
    ) -> CLIResult:
        """
        Execute a CLI subprocess task.

        Args:
            task_type: Type of task (matches prompt template)
            timeout: Timeout in seconds (overrides config)
            **template_vars: Variables for prompt template

        Returns:
            CLIResult with parsed data or error
        """
        if not self.available:
            return CLIResult(
                success=False,
                error="CLI not available - check that claude or gemini CLI is installed",
            )

        try:
            # Generate prompt from template
            prompt = get_prompt(task_type, **template_vars)

            # Execute subprocess with stdin piping (Unix-style)
            start_time = __import__("time").time()

            result = subprocess.run(
                self.config.command,
                input=prompt,  # Pipe prompt via stdin
                capture_output=True,
                text=True,
                timeout=timeout or self.config.timeout,
            )

            execution_time = __import__("time").time() - start_time

            if result.returncode != 0:
                logger.error(f"CLI subprocess failed: {result.stderr}")
                return CLIResult(
                    success=False,
                    error=f"CLI returned non-zero exit code: {result.stderr}",
                    raw_output=result.stdout,
                    execution_time=execution_time,
                )

            # Parse JSON response
            output = result.stdout.strip()

            # Clean output - remove markdown code blocks if present
            if output.startswith("```"):
                # Extract JSON from markdown code block
                lines = output.split("\n")
                output = "\n".join(
                    line
                    for line in lines
                    if not line.strip().startswith("```")
                )

            try:
                data = json.loads(output)
                logger.info(
                    f"CLI subprocess completed in {execution_time:.2f}s: {task_type}"
                )
                return CLIResult(
                    success=True,
                    data=data,
                    raw_output=output,
                    execution_time=execution_time,
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse CLI JSON output: {e}")
                logger.debug(f"Raw output: {output[:500]}")
                return CLIResult(
                    success=False,
                    error=f"Invalid JSON response: {str(e)}",
                    raw_output=output,
                    execution_time=execution_time,
                )

        except subprocess.TimeoutExpired:
            logger.error(f"CLI subprocess timeout after {timeout}s")
            return CLIResult(
                success=False,
                error=f"Timeout after {timeout}s",
            )

        except Exception as e:
            logger.error(f"CLI subprocess error: {str(e)}")
            return CLIResult(
                success=False,
                error=str(e),
            )

    def execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        max_workers: Optional[int] = None,
    ) -> List[CLIResult]:
        """
        Execute multiple CLI tasks in parallel.

        Args:
            tasks: List of task dicts with 'task_type' and template vars
            max_workers: Max parallel workers (defaults to config.max_parallel)

        Returns:
            List of CLIResults in same order as tasks
        """
        if not self.available:
            return [
                CLIResult(success=False, error="CLI not available") for _ in tasks
            ]

        max_workers = max_workers or self.config.max_parallel
        results = [None] * len(tasks)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(self.execute, **task): idx
                for idx, task in enumerate(tasks)
            }

            # Collect results as they complete
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    logger.error(f"Parallel task {idx} failed: {e}")
                    results[idx] = CLIResult(success=False, error=str(e))

        return results

    def is_available(self) -> bool:
        """Check if CLI executor is available"""
        return self.available


# Singleton instance
_cli_executor: Optional[CLIExecutor] = None


def get_cli_executor(model: CLIModel = "auto", reset: bool = False) -> CLIExecutor:
    """
    Get or create CLI executor singleton.

    Args:
        model: CLI model preference
        reset: Force recreate executor

    Returns:
        CLIExecutor instance
    """
    global _cli_executor

    if reset or _cli_executor is None:
        _cli_executor = CLIExecutor(model=model)

    return _cli_executor
