"""
Logging Configuration and Structured Logging (T052)
Provides centralized logging configuration for TRIZ tools.
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class LogConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "json"  # json, text, or structured
    file_path: Optional[Path] = None
    max_bytes: int = 10_485_760  # 10MB
    backup_count: int = 5
    console_output: bool = True
    include_traceback: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.file_path:
            data["file_path"] = str(self.file_path)
        return data


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record
        
        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        
        if hasattr(record, "operation"):
            log_data["operation"] = record.operation
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors.
        
        Args:
            record: Log record
        
        Returns:
            Colored log string
        """
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # Format the message
        result = super().format(record)
        
        # Reset level name for other handlers
        record.levelname = levelname
        
        return result


class ContextFilter(logging.Filter):
    """Add context information to log records"""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """Initialize with optional context"""
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context to record.
        
        Args:
            record: Log record
        
        Returns:
            True to pass the record
        """
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class LoggerManager:
    """Manages logger configuration and setup"""
    
    _instance: Optional['LoggerManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'LoggerManager':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger manager"""
        if not self._initialized:
            self.config = LogConfig()
            self.loggers: Dict[str, logging.Logger] = {}
            self.handlers: Dict[str, logging.Handler] = {}
            self._initialized = True
    
    def setup(
        self,
        config: Optional[LogConfig] = None,
        log_dir: Optional[Path] = None
    ) -> None:
        """
        Setup logging configuration.
        
        Args:
            config: Logging configuration
            log_dir: Directory for log files
        """
        if config:
            self.config = config
        
        # Set up log directory
        if log_dir and not self.config.file_path:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            self.config.file_path = log_dir / f"triz_{datetime.now():%Y%m%d}.log"
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler
        if self.config.console_output:
            console_handler = self._create_console_handler()
            root_logger.addHandler(console_handler)
            self.handlers["console"] = console_handler
        
        # Add file handler
        if self.config.file_path:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
            self.handlers["file"] = file_handler
        
        # Configure specific loggers
        self._configure_module_loggers()
    
    def _create_console_handler(self) -> logging.Handler:
        """Create console handler with appropriate formatter"""
        handler = logging.StreamHandler(sys.stdout)
        
        if self.config.format == "json":
            formatter = StructuredFormatter()
        elif self.config.format == "structured":
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:  # text format with colors
            formatter = ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    def _create_file_handler(self) -> logging.Handler:
        """Create rotating file handler"""
        if not self.config.file_path:
            raise ValueError("File path not configured")
        
        # Ensure directory exists
        self.config.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=str(self.config.file_path),
            maxBytes=self.config.max_bytes,
            backupCount=self.config.backup_count
        )
        
        # Always use structured format for files
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        
        return handler
    
    def _configure_module_loggers(self) -> None:
        """Configure specific module loggers"""
        # Reduce noise from third-party libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("ollama").setLevel(logging.INFO)
        logging.getLogger("qdrant_client").setLevel(logging.WARNING)
        
        # Configure TRIZ module loggers
        triz_modules = [
            "triz_tools",
            "triz_tools.services",
            "triz_tools.models",
            "triz_tools.setup"
        ]
        
        for module_name in triz_modules:
            logger = logging.getLogger(module_name)
            logger.setLevel(getattr(logging, self.config.level))
            self.loggers[module_name] = logger
    
    def get_logger(
        self,
        name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> logging.Logger:
        """
        Get configured logger.
        
        Args:
            name: Logger name
            context: Optional context to add
        
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        if context:
            context_filter = ContextFilter(context)
            logger.addFilter(context_filter)
        
        self.loggers[name] = logger
        return logger
    
    def add_context(
        self,
        logger: Union[str, logging.Logger],
        context: Dict[str, Any]
    ) -> None:
        """
        Add context to logger.
        
        Args:
            logger: Logger name or instance
            context: Context to add
        """
        if isinstance(logger, str):
            logger = logging.getLogger(logger)
        
        context_filter = ContextFilter(context)
        logger.addFilter(context_filter)
    
    def log_operation(
        self,
        operation: str,
        start_time: float,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Log an operation with timing.
        
        Args:
            operation: Operation name
            start_time: Start timestamp
            success: Whether operation succeeded
            details: Additional details
            logger: Logger to use
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        
        duration_ms = (datetime.now().timestamp() - start_time) * 1000
        
        log_data = {
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            "success": success
        }
        
        if details:
            log_data.update(details)
        
        # Add as extra fields
        extra = {key: value for key, value in log_data.items()}
        
        if success:
            logger.info(
                f"Operation completed: {operation} ({duration_ms:.2f}ms)",
                extra=extra
            )
        else:
            logger.error(
                f"Operation failed: {operation} ({duration_ms:.2f}ms)",
                extra=extra
            )
    
    def get_config(self) -> LogConfig:
        """Get current configuration"""
        return self.config
    
    def update_level(self, level: str) -> None:
        """
        Update logging level.
        
        Args:
            level: New logging level
        """
        self.config.level = level
        
        # Update root logger
        logging.getLogger().setLevel(getattr(logging, level))
        
        # Update module loggers
        for logger in self.loggers.values():
            logger.setLevel(getattr(logging, level))
    
    def rotate_logs(self) -> None:
        """Force rotation of file logs"""
        if "file" in self.handlers:
            handler = self.handlers["file"]
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.doRollover()


# Singleton instance
_logger_manager: Optional[LoggerManager] = None


def get_logger_manager() -> LoggerManager:
    """Get or create logger manager"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def setup_logging(
    level: str = "INFO",
    format: str = "text",
    log_dir: Optional[Path] = None,
    console: bool = True
) -> None:
    """
    Quick setup for logging.
    
    Args:
        level: Logging level
        format: Output format (json, text, structured)
        log_dir: Directory for log files
        console: Whether to output to console
    """
    config = LogConfig(
        level=level,
        format=format,
        console_output=console
    )
    
    manager = get_logger_manager()
    manager.setup(config, log_dir)


def get_logger(
    name: str,
    context: Optional[Dict[str, Any]] = None
) -> logging.Logger:
    """
    Get configured logger.
    
    Args:
        name: Logger name
        context: Optional context
    
    Returns:
        Configured logger
    """
    manager = get_logger_manager()
    return manager.get_logger(name, context)


# Structured logging helpers
class LogContext:
    """Context manager for structured logging"""
    
    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        **context
    ):
        """Initialize log context"""
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        """Enter context"""
        self.start_time = datetime.now().timestamp()
        self.logger.info(
            f"Starting: {self.operation}",
            extra={"operation": self.operation, **self.context}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        duration_ms = (datetime.now().timestamp() - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.info(
                f"Completed: {self.operation} ({duration_ms:.2f}ms)",
                extra={
                    "operation": self.operation,
                    "duration_ms": duration_ms,
                    "success": True,
                    **self.context
                }
            )
        else:
            self.logger.error(
                f"Failed: {self.operation} ({duration_ms:.2f}ms) - {exc_val}",
                extra={
                    "operation": self.operation,
                    "duration_ms": duration_ms,
                    "success": False,
                    "error": str(exc_val),
                    "error_type": exc_type.__name__,
                    **self.context
                },
                exc_info=True
            )


# Initialize default configuration on import
if __name__ != "__main__":
    setup_logging()