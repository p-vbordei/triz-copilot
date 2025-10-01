"""
Configuration Management (T053)
Centralized configuration for TRIZ tools.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
import yaml

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration"""
    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    qdrant_use_memory: bool = False  # Use in-memory mode
    
    # Collection settings
    vector_size: int = 768  # nomic-embed-text dimension
    distance_metric: str = "cosine"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EmbeddingConfig:
    """Embedding service configuration"""
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "nomic-embed-text"
    
    # Embedding settings
    batch_size: int = 10
    max_retries: int = 3
    timeout: int = 30
    cache_embeddings: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SessionConfig:
    """Session management configuration"""
    storage_dir: Path = field(default_factory=lambda: Path.home() / ".triz_copilot" / "sessions")
    max_sessions: int = 100
    session_timeout_hours: int = 24
    auto_save: bool = True
    cleanup_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["storage_dir"] = str(self.storage_dir)
        return data


@dataclass
class AnalysisConfig:
    """Analysis service configuration"""
    max_principles: int = 5
    min_confidence: float = 0.5
    max_solutions: int = 4
    enable_hybrid_solutions: bool = True
    innovation_weight: float = 0.3
    feasibility_weight: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MaterialsConfig:
    """Materials service configuration"""
    database_file: Optional[Path] = None
    max_recommendations: int = 5
    cost_weight: float = 0.3
    sustainability_weight: float = 0.2
    performance_weight: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.database_file:
            data["database_file"] = str(self.database_file)
        return data


@dataclass
class TRIZConfig:
    """Main TRIZ configuration"""
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    materials: MaterialsConfig = field(default_factory=MaterialsConfig)
    
    # General settings
    debug: bool = False
    log_level: str = "INFO"
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent / "data")
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".triz_copilot" / "cache")
    
    # Feature flags
    enable_vector_search: bool = True
    enable_offline_mode: bool = True
    enable_caching: bool = True
    enable_telemetry: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "database": self.database.to_dict(),
            "embedding": self.embedding.to_dict(),
            "session": self.session.to_dict(),
            "analysis": self.analysis.to_dict(),
            "materials": self.materials.to_dict(),
            "debug": self.debug,
            "log_level": self.log_level,
            "data_dir": str(self.data_dir),
            "cache_dir": str(self.cache_dir),
            "enable_vector_search": self.enable_vector_search,
            "enable_offline_mode": self.enable_offline_mode,
            "enable_caching": self.enable_caching,
            "enable_telemetry": self.enable_telemetry
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TRIZConfig':
        """Create from dictionary"""
        config = cls()
        
        # Parse sub-configurations
        if "database" in data:
            config.database = DatabaseConfig(**data["database"])
        
        if "embedding" in data:
            config.embedding = EmbeddingConfig(**data["embedding"])
        
        if "session" in data:
            session_data = data["session"].copy()
            if "storage_dir" in session_data:
                session_data["storage_dir"] = Path(session_data["storage_dir"])
            config.session = SessionConfig(**session_data)
        
        if "analysis" in data:
            config.analysis = AnalysisConfig(**data["analysis"])
        
        if "materials" in data:
            materials_data = data["materials"].copy()
            if "database_file" in materials_data and materials_data["database_file"]:
                materials_data["database_file"] = Path(materials_data["database_file"])
            config.materials = MaterialsConfig(**materials_data)
        
        # Parse general settings
        if "debug" in data:
            config.debug = data["debug"]
        
        if "log_level" in data:
            config.log_level = data["log_level"]
        
        if "data_dir" in data:
            config.data_dir = Path(data["data_dir"])
        
        if "cache_dir" in data:
            config.cache_dir = Path(data["cache_dir"])
        
        # Parse feature flags
        for flag in ["enable_vector_search", "enable_offline_mode", "enable_caching", "enable_telemetry"]:
            if flag in data:
                setattr(config, flag, data[flag])
        
        return config


class ConfigManager:
    """Manages configuration loading and access"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[TRIZConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize config manager"""
        if self._config is None:
            self._config = TRIZConfig()
            self._config_file: Optional[Path] = None
            self._env_prefix = "TRIZ_"
    
    def load(
        self,
        config_file: Optional[Union[str, Path]] = None,
        use_env: bool = True
    ) -> TRIZConfig:
        """
        Load configuration from file and environment.
        
        Args:
            config_file: Configuration file path
            use_env: Whether to use environment variables
        
        Returns:
            Loaded configuration
        """
        # Start with default config
        self._config = TRIZConfig()
        
        # Load from file if provided
        if config_file:
            self._load_from_file(config_file)
        else:
            # Try default locations
            self._load_from_default_locations()
        
        # Override with environment variables
        if use_env:
            self._load_from_env()
        
        # Create necessary directories
        self._ensure_directories()
        
        logger.info(f"Configuration loaded from {self._config_file or 'defaults'}")
        return self._config
    
    def _load_from_file(self, config_file: Union[str, Path]) -> None:
        """Load configuration from file"""
        config_file = Path(config_file)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}")
            return
        
        try:
            with open(config_file, "r") as f:
                if config_file.suffix == ".json":
                    data = json.load(f)
                elif config_file.suffix in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    logger.warning(f"Unknown config file format: {config_file.suffix}")
                    return
            
            self._config = TRIZConfig.from_dict(data)
            self._config_file = config_file
            logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_file}: {str(e)}")
    
    def _load_from_default_locations(self) -> None:
        """Try loading from default config locations"""
        default_locations = [
            Path.home() / ".triz_copilot" / "config.json",
            Path.home() / ".triz_copilot" / "config.yaml",
            Path.cwd() / "triz_config.json",
            Path.cwd() / "triz_config.yaml",
            Path("/etc/triz_copilot/config.json"),
            Path("/etc/triz_copilot/config.yaml"),
        ]
        
        for location in default_locations:
            if location.exists():
                self._load_from_file(location)
                break
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        # Database settings
        if os.getenv(f"{self._env_prefix}QDRANT_HOST"):
            self._config.database.qdrant_host = os.getenv(f"{self._env_prefix}QDRANT_HOST")
        
        if os.getenv(f"{self._env_prefix}QDRANT_PORT"):
            self._config.database.qdrant_port = int(os.getenv(f"{self._env_prefix}QDRANT_PORT"))
        
        if os.getenv(f"{self._env_prefix}QDRANT_API_KEY"):
            self._config.database.qdrant_api_key = os.getenv(f"{self._env_prefix}QDRANT_API_KEY")
        
        # Ollama settings
        if os.getenv(f"{self._env_prefix}OLLAMA_HOST"):
            self._config.embedding.ollama_host = os.getenv(f"{self._env_prefix}OLLAMA_HOST")
        
        if os.getenv(f"{self._env_prefix}OLLAMA_MODEL"):
            self._config.embedding.ollama_model = os.getenv(f"{self._env_prefix}OLLAMA_MODEL")
        
        # General settings
        if os.getenv(f"{self._env_prefix}DEBUG"):
            self._config.debug = os.getenv(f"{self._env_prefix}DEBUG").lower() in ["true", "1", "yes"]
        
        if os.getenv(f"{self._env_prefix}LOG_LEVEL"):
            self._config.log_level = os.getenv(f"{self._env_prefix}LOG_LEVEL")
        
        # Feature flags
        if os.getenv(f"{self._env_prefix}ENABLE_OFFLINE_MODE"):
            self._config.enable_offline_mode = os.getenv(f"{self._env_prefix}ENABLE_OFFLINE_MODE").lower() in ["true", "1", "yes"]
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        directories = [
            self._config.data_dir,
            self._config.cache_dir,
            self._config.session.storage_dir
        ]
        
        for directory in directories:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)
    
    def save(
        self,
        config_file: Optional[Union[str, Path]] = None,
        format: str = "json"
    ) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_file: Output file path
            format: Output format (json or yaml)
        
        Returns:
            True if successful
        """
        if config_file is None:
            if self._config_file:
                config_file = self._config_file
            else:
                config_file = Path.home() / ".triz_copilot" / f"config.{format}"
        else:
            config_file = Path(config_file)
        
        # Ensure directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = self._config.to_dict()
            
            with open(config_file, "w") as f:
                if format == "json":
                    json.dump(data, f, indent=2)
                elif format == "yaml":
                    yaml.safe_dump(data, f, default_flow_style=False)
                else:
                    logger.error(f"Unknown format: {format}")
                    return False
            
            logger.info(f"Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            return False
    
    def get(self) -> TRIZConfig:
        """Get current configuration"""
        if self._config is None:
            self.load()
        return self._config
    
    def update(
        self,
        section: str,
        **kwargs
    ) -> None:
        """
        Update configuration section.
        
        Args:
            section: Configuration section name
            **kwargs: Configuration values
        """
        if self._config is None:
            self.load()
        
        if hasattr(self._config, section):
            config_section = getattr(self._config, section)
            for key, value in kwargs.items():
                if hasattr(config_section, key):
                    setattr(config_section, key, value)
                else:
                    logger.warning(f"Unknown config key: {section}.{key}")
        else:
            logger.warning(f"Unknown config section: {section}")
    
    def reset(self) -> None:
        """Reset to default configuration"""
        self._config = TRIZConfig()
        self._config_file = None
        logger.info("Configuration reset to defaults")


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create config manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> TRIZConfig:
    """Get current configuration"""
    manager = get_config_manager()
    return manager.get()


def load_config(
    config_file: Optional[Union[str, Path]] = None,
    use_env: bool = True
) -> TRIZConfig:
    """
    Load configuration.
    
    Args:
        config_file: Configuration file path
        use_env: Whether to use environment variables
    
    Returns:
        Loaded configuration
    """
    manager = get_config_manager()
    return manager.load(config_file, use_env)


def save_config(
    config_file: Optional[Union[str, Path]] = None,
    format: str = "json"
) -> bool:
    """
    Save configuration.
    
    Args:
        config_file: Output file path
        format: Output format
    
    Returns:
        True if successful
    """
    manager = get_config_manager()
    return manager.save(config_file, format)


def update_config(section: str, **kwargs) -> None:
    """
    Update configuration section.
    
    Args:
        section: Section name
        **kwargs: Configuration values
    """
    manager = get_config_manager()
    manager.update(section, **kwargs)


# Create default config file if it doesn't exist
def create_default_config() -> None:
    """Create default configuration file"""
    default_path = Path.home() / ".triz_copilot" / "config.json"
    
    if not default_path.exists():
        config = TRIZConfig()
        manager = get_config_manager()
        manager._config = config
        manager.save(default_path, "json")
        print(f"Created default configuration at {default_path}")


if __name__ == "__main__":
    # Create default config when run as script
    create_default_config()